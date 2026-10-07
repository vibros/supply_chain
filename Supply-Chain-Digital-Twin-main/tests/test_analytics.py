"""
Unit tests for Phase 5 Cost Engine & Resilience KPIs.
"""

import pytest
import pandas as pd

from src.analytics.cost import CostEngine, CostParameters
from src.analytics.kpi import ResilienceEngine
from src.network import create_default_pipeline
from src.demand import DemandEngine, DemandConfig, DemandPattern
from src.simulation.engine import SupplyChainSimulation


def test_cost_engine_calculation():
    params = CostParameters(holding_cost_per_unit_day=1.0, backlog_penalty_per_unit_day=5.0)
    engine = CostEngine(params)

    # Mock dataframe snapshot
    df_mock = pd.DataFrame([
        {"day": 1, "inventory": 100.0, "backlog": 0.0},
        {"day": 2, "inventory": 50.0, "backlog": 20.0},
    ])

    breakdown = engine.compute_costs(df_mock)
    # Holding: 100*1 + 50*1 = 150
    # Backlog: 0*5 + 20*5 = 100
    # Total: 250
    assert breakdown.total_holding_cost == 150.0
    assert breakdown.total_backlog_cost == 100.0
    assert breakdown.total_operating_cost == 250.0


def test_resilience_engine_metrics():
    net = create_default_pipeline()
    d_cfg = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=500.0)
    d_engine = DemandEngine(d_cfg)
    sim = SupplyChainSimulation(network=net, demand_engine=d_engine, horizon_days=10)
    df = sim.run().to_dataframe()

    metrics = ResilienceEngine.calculate_metrics(df)
    assert metrics.service_level_pct >= 0.0
    assert metrics.resilience_score >= 0.0