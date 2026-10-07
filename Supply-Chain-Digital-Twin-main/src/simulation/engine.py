"""
Discrete-Event Simulation Engine using SimPy with Disruption Engine Integration.
"""

import simpy
from typing import Dict, Any, List, Optional
import numpy as np

from src.network import SupplyChainNetwork
from src.simulation.entities import NodeType, Customer, Warehouse, Factory, Supplier, DistributionCenter
from src.simulation.state import SimulationState, DailyNodeSnapshot
from src.simulation.events import Shipment
from src.demand import DemandEngine
from src.disruptions import DisruptionEngine


class SupplyChainSimulation:
    def __init__(
        self,
        network: SupplyChainNetwork,
        demand_engine: DemandEngine,
        disruption_engine: Optional[DisruptionEngine] = None,
        horizon_days: int = 90,
    ):
        self.network = network
        self.demand_engine = demand_engine
        self.disruption_engine = disruption_engine
        self.horizon_days = horizon_days
        self.env = simpy.Environment()
        self.state = SimulationState()
        self.demand_series = self.demand_engine.generate_demand(self.horizon_days)

        # Initialize disruption baseline snapshot if disruption engine is present
        if self.disruption_engine:
            self.disruption_engine.store_baselines(self.network)

    def _daily_simulation_loop(self):
        """Main daily clock cycle process executed every timestep."""
        for day in range(1, self.horizon_days + 1):
            # Apply dynamic active disruptions for the current day
            if self.disruption_engine:
                self.disruption_engine.apply_disruptions_for_day(self.network, current_day=day)

            current_demand = self.demand_series[day - 1]

            # 1. Process Customer Demand & Backlog Fulfillment
            customers = self.network.get_nodes_by_type(NodeType.CUSTOMER)
            dcs = self.network.get_nodes_by_type(NodeType.DISTRIBUTION_CENTER)
            warehouses = self.network.get_nodes_by_type(NodeType.WAREHOUSE)
            factories = self.network.get_nodes_by_type(NodeType.FACTORY)

            for cust in customers:
                assert isinstance(cust, Customer)
                active_demand = getattr(cust, "daily_demand", current_demand)
                cust.total_requested_demand += active_demand
                total_unfulfilled = active_demand + cust.current_backlog

                fulfilled_today = 0.0
                for dc in dcs:
                    assert isinstance(dc, DistributionCenter)
                    fulfillable = min(dc.current_inventory, total_unfulfilled - fulfilled_today)
                    if fulfillable > 0:
                        dc.current_inventory -= fulfillable
                        fulfilled_today += fulfillable

                cust.fulfilled_demand += fulfilled_today
                cust.current_backlog = total_unfulfilled - fulfilled_today

            # 2. Process Replenishment Orders
            for dc in dcs:
                assert isinstance(dc, DistributionCenter)
                if dc.current_inventory < 1000.0:
                    for wh in warehouses:
                        assert isinstance(wh, Warehouse)
                        transfer = min(wh.current_inventory, 500.0)
                        if transfer > 0:
                            wh.current_inventory -= transfer
                            dc.current_inventory += transfer

            # 3. Process Factory Production
            for fac in factories:
                assert isinstance(fac, Factory)
                cap = getattr(fac, "production_capacity_per_day", 800.0)
                produced = min(cap, 800.0)
                if produced > 0:
                    for wh in warehouses:
                        assert isinstance(wh, Warehouse)
                        avail_space = wh.storage_capacity - wh.current_inventory
                        stored = min(produced, avail_space)
                        wh.current_inventory += stored

            # 4. Log Daily Snapshots
            for _, data in self.network.graph.nodes(data=True):
                entity = data["entity"]
                inv = getattr(entity, "current_inventory", 0.0)
                backlog = getattr(entity, "current_backlog", 0.0)
                fulfilled = getattr(entity, "fulfilled_demand", 0.0)
                total_req = getattr(entity, "total_requested_demand", 0.0)

                self.state.record_node_snapshot(
                    DailyNodeSnapshot(
                        day=day,
                        node_id=entity.node_id,
                        inventory=inv,
                        backlog=backlog,
                        fulfilled_demand=fulfilled,
                        requested_demand=total_req,
                    )
                )

            yield self.env.timeout(1)

    def run(self) -> SimulationState:
        """Executes the simulation engine and returns state records."""
        self.env.process(self._daily_simulation_loop())
        self.env.run(until=self.horizon_days)
        return self.state