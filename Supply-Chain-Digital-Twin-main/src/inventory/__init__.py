"""
Inventory Management Module Exports.
"""

from src.inventory.policies import InventoryPolicy, PolicyType, PolicyEngine
from src.inventory.safety_stock import SafetyStockCalculator, SafetyStockConfig

# Backward compatibility alias
CalculateSafetyStock = SafetyStockCalculator

__all__ = [
    "InventoryPolicy",
    "PolicyType",
    "PolicyEngine",
    "SafetyStockCalculator",
    "SafetyStockConfig",
    "CalculateSafetyStock",
]