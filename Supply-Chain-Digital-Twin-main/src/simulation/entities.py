"""
Domain entities representing nodes in the Supply Chain Digital Twin.
All state variables, capacity limits, and unit operational metrics are tracked here.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any


class NodeStatus(Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    DISRUPTED = "DISRUPTED"


class NodeType(Enum):
    SUPPLIER = "SUPPLIER"
    FACTORY = "FACTORY"
    WAREHOUSE = "WAREHOUSE"
    DISTRIBUTION_CENTER = "DISTRIBUTION_CENTER"
    CUSTOMER = "CUSTOMER"


@dataclass
class BaseNode:
    node_id: str
    name: str
    node_type: NodeType
    status: NodeStatus = NodeStatus.NORMAL

    def __post_init__(self):
        if not self.node_id or not self.name:
            raise ValueError("node_id and name must be non-empty strings.")

    def set_status(self, status: NodeStatus) -> None:
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type.value,
            "status": self.status.value,
        }


@dataclass
class Supplier(BaseNode):
    node_type: NodeType = field(default=NodeType.SUPPLIER, init=False)
    capacity_per_day: float = 1000.0
    lead_time_days: float = 3.0
    unit_cost: float = 100.0
    reliability: float = 0.98

    def __post_init__(self):
        super().__post_init__()
        if self.capacity_per_day < 0:
            raise ValueError("capacity_per_day must be non-negative.")
        if self.lead_time_days < 0:
            raise ValueError("lead_time_days must be non-negative.")
        if self.unit_cost < 0:
            raise ValueError("unit_cost must be non-negative.")
        if not (0.0 <= self.reliability <= 1.0):
            raise ValueError("reliability must be between 0.0 and 1.0.")


@dataclass
class Factory(BaseNode):
    node_type: NodeType = field(default=NodeType.FACTORY, init=False)
    production_capacity_per_day: float = 1000.0
    production_lead_time_days: float = 2.0
    production_unit_cost: float = 150.0
    current_inventory: float = 0.0
    max_raw_material_capacity: float = 5000.0

    def __post_init__(self):
        super().__post_init__()
        if self.production_capacity_per_day < 0:
            raise ValueError("production_capacity_per_day must be non-negative.")
        if self.production_lead_time_days < 0:
            raise ValueError("production_lead_time_days must be non-negative.")
        if self.current_inventory < 0:
            raise ValueError("current_inventory cannot be negative.")


@dataclass
class Warehouse(BaseNode):
    node_type: NodeType = field(default=NodeType.WAREHOUSE, init=False)
    storage_capacity: float = 10000.0
    current_inventory: float = 2000.0
    holding_cost_per_unit_day: float = 1.5
    reorder_point: float = 1000.0
    reorder_quantity: float = 2000.0

    def __post_init__(self):
        super().__post_init__()
        if self.storage_capacity < 0:
            raise ValueError("storage_capacity must be non-negative.")
        if not (0.0 <= self.current_inventory <= self.storage_capacity):
            raise ValueError("current_inventory must be between 0 and storage_capacity.")


@dataclass
class DistributionCenter(BaseNode):
    node_type: NodeType = field(default=NodeType.DISTRIBUTION_CENTER, init=False)
    throughput_capacity_per_day: float = 3000.0
    current_inventory: float = 1500.0
    max_storage_capacity: float = 5000.0
    holding_cost_per_unit_day: float = 2.0
    transportation_cost_per_unit: float = 10.0

    def __post_init__(self):
        super().__post_init__()
        if self.throughput_capacity_per_day < 0:
            raise ValueError("throughput_capacity_per_day must be non-negative.")
        if not (0.0 <= self.current_inventory <= self.max_storage_capacity):
            raise ValueError("current_inventory must be within max_storage_capacity.")


@dataclass
class Customer(BaseNode):
    node_type: NodeType = field(default=NodeType.CUSTOMER, init=False)
    daily_demand: float = 500.0
    current_backlog: float = 0.0
    fulfilled_demand: float = 0.0
    total_requested_demand: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        if self.daily_demand < 0:
            raise ValueError("daily_demand must be non-negative.")

    @property
    def fill_rate(self) -> float:
        if self.total_requested_demand == 0.0:
            return 1.0
        return self.fulfilled_demand / self.total_requested_demand