"""
Inventory Policies and Policy Evaluation Engine.
"""

from dataclasses import dataclass
from enum import Enum


class PolicyType(Enum):
    CONTINUOUS_REVIEW = "CONTINUOUS_REVIEW"  # (s, Q) policy
    PERIODIC_REVIEW = "PERIODIC_REVIEW"      # (R, S) policy
    MIN_MAX = "MIN_MAX"                      # (s, S) policy


@dataclass
class InventoryPolicy:
    policy_type: PolicyType
    reorder_point: float
    order_quantity: float
    target_inventory_level: float
    safety_stock: float


class PolicyEngine:
    def __init__(self, policy: InventoryPolicy):
        self.policy = policy

    def evaluate_reorder(self, current_inventory: float, current_backlog: float = 0.0) -> float:
        """
        Evaluates current inventory position and returns order quantity if reorder condition is met.
        Inventory Position = On-Hand Inventory - Backlog
        """
        inventory_position = current_inventory - current_backlog

        if inventory_position <= self.policy.reorder_point:
            if self.policy.policy_type == PolicyType.CONTINUOUS_REVIEW:
                return self.policy.order_quantity
            elif self.policy.policy_type in (PolicyType.PERIODIC_REVIEW, PolicyType.MIN_MAX):
                return max(0.0, self.policy.target_inventory_level - inventory_position)
        return 0.0