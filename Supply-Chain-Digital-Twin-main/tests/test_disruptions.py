"""
Unit tests for Phase 4 Disruption Engine & Impact Propagation.
"""

import pytest
from src.network import create_default_pipeline
from src.demand import DemandEngine, DemandConfig, DemandPattern
from src.disruptions import DisruptionEngine, Disruption, DisruptionType
from src.simulation.engine import SupplyChainSimulation
from src.simulation.entities import NodeStatus


def test_disruption_lifecycle():
    net = create_default_pipeline()
    d_engine = DisruptionEngine()

    disruption = Disruption(
        disruption_id="DIS_01",
        disruption_type=DisruptionType.FACILITY_SHUTDOWN,
        affected_node_id="FAC_01",
        start_day=5,
        duration_days=5,
    )
    d_engine.add_disruption(disruption)
    d_engine.store_baselines(net)

    # Before start_day -> Normal
    statuses_day1 = d_engine.apply_disruptions_for_day(net, current_day=1)
    assert statuses_day1["FAC_01"] == NodeStatus.NORMAL

    # Active window -> Disrupted
    statuses_day5 = d_engine.apply_disruptions_for_day(net, current_day=5)
    assert statuses_day5["FAC_01"] == NodeStatus.DISRUPTED
    assert net.get_node("FAC_01").production_capacity_per_day == 0.0

    # After end_day -> Restored to Normal
    statuses_day11 = d_engine.apply_disruptions_for_day(net, current_day=11)
    assert statuses_day11["FAC_01"] == NodeStatus.NORMAL
    assert net.get_node("FAC_01").production_capacity_per_day > 0.0


def test_disruption_impact_on_simulation():
    net = create_default_pipeline()
    demand_cfg = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=500.0)
    demand_engine = DemandEngine(demand_cfg)

    d_engine = DisruptionEngine([
        Disruption(
            disruption_id="DIS_DC",
            disruption_type=DisruptionType.CAPACITY_REDUCTION,
            affected_node_id="FAC_01",
            start_day=2,
            duration_days=10,
            magnitude=0.0,
        )
    ])

    sim = SupplyChainSimulation(
        network=net,
        demand_engine=demand_engine,
        disruption_engine=d_engine,
        horizon_days=20
    )
    state = sim.run()
    df = state.to_dataframe()

    assert not df.empty
    assert "backlog" in df.columns