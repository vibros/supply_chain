"""
State Tracker for Supply Chain Simulation.
Records daily snapshots across all nodes in the network.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd


@dataclass
class DailyNodeSnapshot:
    day: int
    node_id: str
    inventory: float
    backlog: float
    fulfilled_demand: float
    requested_demand: float
    production_output: float = 0.0


class SimulationState:
    def __init__(self):
        self.snapshots: List[DailyNodeSnapshot] = []
        self.shipments_in_transit: List[Dict[str, Any]] = []

    def record_node_snapshot(self, snapshot: DailyNodeSnapshot) -> None:
        self.snapshots.append(snapshot)

    def record_shipment(self, shipment: Dict[str, Any]) -> None:
        self.shipments_in_transit.append(shipment)

    def to_dataframe(self) -> pd.DataFrame:
        if not self.snapshots:
            return pd.DataFrame()
        records = [s.__dict__ for s in self.snapshots]
        return pd.DataFrame(records)