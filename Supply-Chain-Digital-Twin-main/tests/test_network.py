"""
Unit testing suite for Phase 1 entities and SupplyChainNetwork configuration.
"""

import pytest
from src.simulation.entities import Supplier, Factory, Customer, Warehouse, DistributionCenter, NodeStatus
from src.network import SupplyChainNetwork, create_default_pipeline


def test_supplier_entity_validation():
    s = Supplier("S1", "Supplier 1", capacity_per_day=500, reliability=0.95)
    assert s.node_id == "S1"
    assert s.status == NodeStatus.NORMAL

    with pytest.raises(ValueError):
        Supplier("S2", "Bad Supplier", reliability=1.5)

    with pytest.raises(ValueError):
        Supplier("S3", "Negative Capacity", capacity_per_day=-10)


def test_customer_fill_rate():
    c = Customer("C1", "Cust 1", daily_demand=100)
    assert c.fill_rate == 1.0

    c.total_requested_demand = 200.0
    c.fulfilled_demand = 150.0
    assert c.fill_rate == 0.75


def test_network_validation_success():
    net = create_default_pipeline()
    assert net.validate_network() is True
    assert len(net.graph.nodes()) == 5
    assert len(net.graph.edges()) == 4


def test_network_cycle_detection():
    net = SupplyChainNetwork()
    s = Supplier("S1", "Sup")
    f = Factory("F1", "Fac")
    c = Customer("C1", "Cust")

    net.add_node(s)
    net.add_node(f)
    net.add_node(c)

    net.add_edge("S1", "F1")
    net.add_edge("F1", "C1")
    net.add_edge("C1", "S1")

    with pytest.raises(ValueError, match="contains cycles"):
        net.validate_network()


def test_network_disconnected_validation():
    net = SupplyChainNetwork()
    s = Supplier("S1", "Sup")
    c = Customer("C1", "Cust")

    net.add_node(s)
    net.add_node(c)

    with pytest.raises(ValueError, match="No viable routing path exists"):
        net.validate_network()