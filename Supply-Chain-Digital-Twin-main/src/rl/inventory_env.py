"""
Gym-Compatible Multi-Echelon Supply Chain Inventory Environment.
"""

from typing import Dict, Tuple, Any
import numpy as np

from src.network import create_default_pipeline, SupplyChainNetwork
from src.simulation.entities import NodeType, DistributionCenter, Factory, Customer


class SupplyChainInventoryEnv:
    """
    State Space: [DC Inventory, Factory Inventory, Customer Backlog]
    Action Space: Discrete Order Quantities [0, 100, 300, 500, 800]
    Reward: -(Holding Cost + Stockout Penalty Cost)
    """

    ACTION_MAP = [0.0, 100.0, 300.0, 500.0, 800.0]

    def __init__(self, horizon_days: int = 30):
        self.horizon_days = horizon_days
        self.current_day = 0
        self.network: SupplyChainNetwork = create_default_pipeline()

        self.holding_cost_rate = 0.50
        self.penalty_cost_rate = 3.00

    def reset(self) -> np.ndarray:
        """Resets network state and returns initial observation vector."""
        self.current_day = 1
        self.network = create_default_pipeline()
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        dc = self.network.get_node("DC_01")
        fac = self.network.get_node("FAC_01")
        cust = self.network.get_node("CUST_01")

        dc_inv = getattr(dc, "current_inventory", 0.0)
        fac_inv = getattr(fac, "current_inventory", 0.0)
        cust_backlog = getattr(cust, "current_backlog", 0.0)

        return np.array([dc_inv, fac_inv, cust_backlog], dtype=np.float32)

    def step(self, action_idx: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        Executes one day timestep applying chosen action order quantity.
        """
        order_qty = self.ACTION_MAP[action_idx]

        dc = self.network.get_node("DC_01")
        fac = self.network.get_node("FAC_01")
        cust = self.network.get_node("CUST_01")

        # Process factory replenishment to DC
        transfer_qty = min(getattr(fac, "current_inventory", 0.0), order_qty)
        fac.current_inventory -= transfer_qty
        dc.current_inventory += transfer_qty

        # Process Customer Demand
        daily_demand = 500.0
        total_demand = daily_demand + cust.current_backlog
        fulfilled = min(dc.current_inventory, total_demand)

        dc.current_inventory -= fulfilled
        cust.current_backlog = total_demand - fulfilled

        # Factory daily production
        fac.current_inventory = min(5000.0, fac.current_inventory + 600.0)

        # Compute Step Costs & Reward
        holding_cost = (dc.current_inventory + fac.current_inventory) * self.holding_cost_rate
        penalty_cost = cust.current_backlog * self.penalty_cost_rate
        reward = -(holding_cost + penalty_cost)

        self.current_day += 1
        done = self.current_day >= self.horizon_days

        obs = self._get_observation()
        info = {
            "day": self.current_day,
            "fulfilled_demand": fulfilled,
            "holding_cost": holding_cost,
            "penalty_cost": penalty_cost,
        }

        return obs, reward, done, info