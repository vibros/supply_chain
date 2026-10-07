"""
Disruption Engine for Supply Chain Digital Twin.
Defines time-bound disruption events and handles dynamic network state updates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from src.network import SupplyChainNetwork
from src.simulation.entities import NodeStatus, Supplier, Factory, Warehouse, DistributionCenter, Customer


class DisruptionType(Enum):
    SUPPLIER_FAILURE = "SUPPLIER_FAILURE"           # 100% capacity loss
    CAPACITY_REDUCTION = "CAPACITY_REDUCTION"       # Fractional capacity reduction
    LEAD_TIME_INCREASE = "LEAD_TIME_INCREASE"       # Lead time multiplier or offset
    DEMAND_SPIKE = "DEMAND_SPIKE"                   # Demand multiplier (e.g., 2.0 = +100%)
    FACILITY_SHUTDOWN = "FACILITY_SHUTDOWN"         # Complete facility closure


@dataclass
class Disruption:
    disruption_id: str
    disruption_type: DisruptionType
    affected_node_id: str
    start_day: int
    duration_days: int
    magnitude: float = 0.0  # e.g., 0.2 = 20% remaining capacity, 2.0 = 200% demand
    description: str = ""

    def __post_init__(self):
        if self.start_day < 1:
            raise ValueError("start_day must be >= 1.")
        if self.duration_days < 1:
            raise ValueError("duration_days must be >= 1.")

    @property
    def end_day(self) -> int:
        return self.start_day + self.duration_days - 1

    def is_active(self, current_day: int) -> bool:
        return self.start_day <= current_day <= self.end_day


class DisruptionEngine:
    def __init__(self, disruptions: Optional[List[Disruption]] = None):
        self.disruptions: List[Disruption] = disruptions or []
        # Store original node attribute baselines for restoration
        self._node_baselines: Dict[str, Dict[str, Any]] = {}

    def add_disruption(self, disruption: Disruption) -> None:
        self.disruptions.append(disruption)

    def store_baselines(self, network: SupplyChainNetwork) -> None:
        """Captures initial node state values before applying disruptions."""
        self._node_baselines.clear()
        for node_id, data in network.graph.nodes(data=True):
            entity = data["entity"]
            baseline = {}
            if hasattr(entity, "capacity_per_day"):
                baseline["capacity_per_day"] = entity.capacity_per_day
            if hasattr(entity, "production_capacity_per_day"):
                baseline["production_capacity_per_day"] = entity.production_capacity_per_day
            if hasattr(entity, "throughput_capacity_per_day"):
                baseline["throughput_capacity_per_day"] = entity.throughput_capacity_per_day
            if hasattr(entity, "lead_time_days"):
                baseline["lead_time_days"] = entity.lead_time_days
            if hasattr(entity, "daily_demand"):
                baseline["daily_demand"] = entity.daily_demand
            self._node_baselines[node_id] = baseline

    def apply_disruptions_for_day(self, network: SupplyChainNetwork, current_day: int) -> Dict[str, NodeStatus]:
        """
        Evaluates active disruptions for current_day, modifies target node parameters,
        restores original states if a disruption has ended, and returns node status mappings.
        """
        node_statuses: Dict[str, NodeStatus] = {
            node_id: NodeStatus.NORMAL for node_id in network.graph.nodes
        }

        # First, ensure baseline parameters are restored if disruption expired
        for node_id, baseline in self._node_baselines.items():
            if node_id in network.graph:
                entity = network.get_node(node_id)
                for attr, val in baseline.items():
                    setattr(entity, attr, val)

        # Apply active disruptions
        for d in self.disruptions:
            if d.is_active(current_day) and d.affected_node_id in network.graph:
                entity = network.get_node(d.affected_node_id)
                node_statuses[d.affected_node_id] = NodeStatus.DISRUPTED

                if d.disruption_type == DisruptionType.SUPPLIER_FAILURE:
                    if hasattr(entity, "capacity_per_day"):
                        entity.capacity_per_day = 0.0

                elif d.disruption_type == DisruptionType.FACILITY_SHUTDOWN:
                    if hasattr(entity, "production_capacity_per_day"):
                        entity.production_capacity_per_day = 0.0
                    elif hasattr(entity, "throughput_capacity_per_day"):
                        entity.throughput_capacity_per_day = 0.0

                elif d.disruption_type == DisruptionType.CAPACITY_REDUCTION:
                    if hasattr(entity, "capacity_per_day"):
                        baseline_val = self._node_baselines[d.affected_node_id]["capacity_per_day"]
                        entity.capacity_per_day = baseline_val * d.magnitude
                    elif hasattr(entity, "production_capacity_per_day"):
                        baseline_val = self._node_baselines[d.affected_node_id]["production_capacity_per_day"]
                        entity.production_capacity_per_day = baseline_val * d.magnitude

                elif d.disruption_type == DisruptionType.LEAD_TIME_INCREASE:
                    if hasattr(entity, "lead_time_days"):
                        baseline_val = self._node_baselines[d.affected_node_id]["lead_time_days"]
                        entity.lead_time_days = baseline_val * d.magnitude

                elif d.disruption_type == DisruptionType.DEMAND_SPIKE:
                    if hasattr(entity, "daily_demand"):
                        baseline_val = self._node_baselines[d.affected_node_id]["daily_demand"]
                        entity.daily_demand = baseline_val * d.magnitude

        # Update node status properties
        for node_id, status in node_statuses.items():
            network.get_node(node_id).set_status(status)

        return node_statuses