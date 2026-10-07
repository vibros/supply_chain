"""
Supply Chain Network Graph Container.
Manages network topology, edge transport metrics, and execution paths.
"""

from typing import Dict, List, Optional, Type
import networkx as nx

from src.simulation.entities import (
    BaseNode,
    Supplier,
    Factory,
    Warehouse,
    DistributionCenter,
    Customer,
    NodeType,
)


class SupplyChainNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: BaseNode) -> None:
        if node.node_id in self.graph:
            raise ValueError(f"Node with ID '{node.node_id}' already exists in network.")
        self.graph.add_node(node.node_id, entity=node)

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        lead_time_days: float = 1.0,
        transit_cost_per_unit: float = 5.0,
        capacity: float = 10000.0,
    ) -> None:
        if source_id not in self.graph:
            raise KeyError(f"Source node '{source_id}' does not exist.")
        if target_id not in self.graph:
            raise KeyError(f"Target node '{target_id}' does not exist.")
        if lead_time_days < 0 or transit_cost_per_unit < 0 or capacity < 0:
            raise ValueError("Edge parameters must be non-negative.")

        self.graph.add_edge(
            source_id,
            target_id,
            lead_time_days=lead_time_days,
            transit_cost_per_unit=transit_cost_per_unit,
            capacity=capacity,
        )

    def get_node(self, node_id: str) -> BaseNode:
        if node_id not in self.graph:
            raise KeyError(f"Node '{node_id}' not found in network.")
        return self.graph.nodes[node_id]["entity"]

    def get_nodes_by_type(self, node_type: NodeType) -> List[BaseNode]:
        return [
            data["entity"]
            for _, data in self.graph.nodes(data=True)
            if data["entity"].node_type == node_type
        ]

    def validate_network(self) -> bool:
        """
        Validates that the network is non-empty, contains no cycles, and has a valid path from 
        at least one Supplier down to a Customer.
        """
        if self.graph.number_of_nodes() == 0:
            raise ValueError("Network is empty.")

        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Supply chain network contains cycles. Topologies must be DAGs.")

        suppliers = self.get_nodes_by_type(NodeType.SUPPLIER)
        customers = self.get_nodes_by_type(NodeType.CUSTOMER)

        if not suppliers:
            raise ValueError("Network must contain at least one Supplier.")
        if not customers:
            raise ValueError("Network must contain at least one Customer.")

        # Ensure at least one route exists from any supplier to any customer
        has_path = False
        for sup in suppliers:
            for cust in customers:
                if nx.has_path(self.graph, sup.node_id, cust.node_id):
                    has_path = True
                    break
            if has_path:
                break

        if not has_path:
            raise ValueError("No viable routing path exists from Supplier to Customer.")

        return True

    def get_network_summary(self) -> Dict[str, int]:
        summary = {nt.value: 0 for nt in NodeType}
        for _, data in self.graph.nodes(data=True):
            summary[data["entity"].node_type.value] += 1
        return summary


def create_default_pipeline() -> SupplyChainNetwork:
    """
    Constructs the standard baseline 5-tier linear supply chain network:
    Supplier -> Factory -> Warehouse -> Distribution Center -> Customer
    """
    net = SupplyChainNetwork()

    s1 = Supplier(node_id="SUP_01", name="Global Raw Materials Co.", capacity_per_day=1500, lead_time_days=3)
    f1 = Factory(node_id="FAC_01", name="Central Manufacturing Plant", production_capacity_per_day=1200)
    w1 = Warehouse(node_id="WRH_01", name="Regional Fulfillment Hub", storage_capacity=15000, current_inventory=4000)
    dc1 = DistributionCenter(node_id="DC_01", name="Metro Distribution Center", throughput_capacity_per_day=2000, current_inventory=2500)
    c1 = Customer(node_id="CUST_01", name="Tier-1 Retail Network", daily_demand=800)

    net.add_node(s1)
    net.add_node(f1)
    net.add_node(w1)
    net.add_node(dc1)
    net.add_node(c1)

    net.add_edge("SUP_01", "FAC_01", lead_time_days=3.0, transit_cost_per_unit=12.0)
    net.add_edge("FAC_01", "WRH_01", lead_time_days=2.0, transit_cost_per_unit=8.0)
    net.add_edge("WRH_01", "DC_01", lead_time_days=1.0, transit_cost_per_unit=5.0)
    net.add_edge("DC_01", "CUST_01", lead_time_days=1.0, transit_cost_per_unit=3.0)

    net.validate_network()
    return net