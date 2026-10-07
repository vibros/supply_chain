"""
Plotly visualization engine for supply chain network topology rendering.
"""

import plotly.graph_objects as go
import networkx as nx
from src.network import SupplyChainNetwork
from src.simulation.entities import NodeType, NodeStatus


def render_network_graph(network: SupplyChainNetwork) -> go.Figure:
    G = network.graph

    # Horizontal multi-tier layout mapping
    tier_x = {
        NodeType.SUPPLIER: 0.0,
        NodeType.FACTORY: 1.0,
        NodeType.WAREHOUSE: 2.0,
        NodeType.DISTRIBUTION_CENTER: 3.0,
        NodeType.CUSTOMER: 4.0,
    }

    # Group nodes by type to compute y positions
    nodes_by_type = {}
    for node_id, data in G.nodes(data=True):
        ntype = data["entity"].node_type
        nodes_by_type.setdefault(ntype, []).append(node_id)

    pos = {}
    for ntype, node_ids in nodes_by_type.items():
        x = tier_x.get(ntype, 0.0)
        count = len(node_ids)
        for idx, nid in enumerate(node_ids):
            # Centered vertical offset
            y = (idx - (count - 1) / 2.0) * 1.5
            pos[nid] = (x, y)

    # Edge visual traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color="#888888"),
        hoverinfo="none",
        mode="lines",
    )

    # Node visual traces
    status_color_map = {
        NodeStatus.NORMAL.value: "#10B981",    # Emerald Green
        NodeStatus.WARNING.value: "#F59E0B",   # Amber
        NodeStatus.DISRUPTED.value: "#EF4444", # Coral Red
    }

    node_x, node_y, node_colors, node_text, node_labels = [], [], [], [], []

    for node_id, data in G.nodes(data=True):
        entity = data["entity"]
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        node_colors.append(status_color_map[entity.status.value])
        node_labels.append(f"<b>{entity.node_id}</b>")

        hover_info = (
            f"<b>{entity.name}</b> ({entity.node_id})<br>"
            f"Type: {entity.node_type.value}<br>"
            f"Status: {entity.status.value}"
        )
        node_text.append(hover_info)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_labels,
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            size=36,
            color=node_colors,
            line=dict(width=2, color="#1F2937"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="Supply Chain Network Topology (Digital Twin Graph)",
                font=dict(size=18),
            ),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        ),
    )

    return fig