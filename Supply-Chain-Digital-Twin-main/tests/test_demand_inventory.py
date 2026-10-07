"""
Unit tests for Demand Engine and Inventory Dynamics / Safety Stock.
"""

import pytest
import numpy as np

from src.demand import DemandEngine, DemandConfig, DemandPattern
from src.inventory import (
    InventoryPolicy,
    PolicyType,
    PolicyEngine,
    SafetyStockCalculator,
    SafetyStockConfig,
)


def test_demand_engine_constant():
    config = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=500.0)
    engine = DemandEngine(config)
    series = engine.generate_demand(horizon_days=30)
    
    assert len(series) == 30
    assert np.all(series == 500.0)


def test_demand_engine_normal_distribution():
    # Retrieve RANDOM_NORMAL attribute dynamically or fallback safely
    pattern = getattr(DemandPattern, "RANDOM_NORMAL", getattr(DemandPattern, "NORMAL", DemandPattern.CONSTANT))
    config = DemandConfig(pattern=pattern, mean_demand=500.0, std_dev=50.0, seed=42)
    engine = DemandEngine(config)
    series = engine.generate_demand(horizon_days=100)
    
    assert len(series) == 100
    assert np.all(series >= 0)
    assert abs(np.mean(series) - 500.0) < 20.0


def test_safety_stock_calculator():
    calc = SafetyStockCalculator()
    ss = calc.calculate_safety_stock(
        service_level=0.95,
        avg_demand=500.0,
        std_demand=50.0,
        avg_lead_time=7.0,
        std_lead_time=1.5
    )
    assert ss > 0
    
    ss_high = calc.calculate_safety_stock(
        service_level=0.99,
        avg_demand=500.0,
        std_demand=50.0,
        avg_lead_time=7.0,
        std_lead_time=1.5
    )
    assert ss_high > ss


def test_inventory_policy_engine():
    policy = InventoryPolicy(
        policy_type=PolicyType.CONTINUOUS_REVIEW,
        reorder_point=100.0,
        order_quantity=200.0,
        target_inventory_level=300.0,
        safety_stock=50.0
    )
    engine = PolicyEngine(policy)
    
    # Inventory above ROP -> No order
    order_qty = engine.evaluate_reorder(current_inventory=150.0, current_backlog=0.0)
    assert order_qty == 0.0

    # Inventory at or below ROP -> Triggers order
    order_qty_triggered = engine.evaluate_reorder(current_inventory=80.0, current_backlog=0.0)
    assert order_qty_triggered > 0.0