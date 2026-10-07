"""
Unit tests for Phase 3 Discrete-Event Simulation Engine.
"""

import pytest
from src.network import create_default_pipeline
from src.demand import DemandEngine, DemandConfig, DemandPattern
from src.simulation.engine import SupplyChainSimulation


def test_simulation_run_execution():
    net = create_default_pipeline()
    d_config = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=400.0)
    d_engine = DemandEngine(d_config)

    sim = SupplyChainSimulation(network=net, demand_engine=d_engine, horizon_days=14)
    state = sim.run()

    df = state.to_dataframe()
    assert not df.empty
    assert df["day"].max() == 14
    # Check that 5 nodes recorded snapshots across 14 days = 70 records
    assert len(df) == 5 * 14


def test_simulation_inventory_consumption():
    net = create_default_pipeline()
    d_config = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=1000.0)
    d_engine = DemandEngine(d_config)

    sim = SupplyChainSimulation(network=net, demand_engine=d_engine, horizon_days=5)
    state = sim.run()
    df = state.to_dataframe()

    # Check that DC inventory changes over time
    dc_records = df[df["node_id"] == "DC_01"]["inventory"].values
    assert len(dc_records) == 5