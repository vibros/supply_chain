"""
Streamlit Web Interface - Supply Chain Digital Twin
Crimson & Slate Creative Light Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.network import create_default_pipeline, SupplyChainNetwork
from src.demand import DemandEngine, DemandConfig, DemandPattern
from src.inventory import InventoryPolicy, PolicyType, SafetyStockCalculator
from src.disruptions import DisruptionEngine, Disruption, DisruptionType
from src.simulation.engine import SupplyChainSimulation
from src.analytics import CostEngine, CostParameters, ResilienceEngine
from src.optimization import MultiEchelonOptimizer, EchelonStageConfig
from src.rl import SupplyChainInventoryEnv, QLearningInventoryAgent
from src.visualization import render_network_graph
from src.data_io import DataIOEngine
from src.scenario import ScenarioManager

# Page Configuration
st.set_page_config(
    page_title="Supply Chain Digital Twin",
    page_icon="📦",
    layout="wide"
)

# --- CREATIVE LIGHT BACKGROUND & CARD STYLING ---
st.markdown("""
<style>
    /* Ambient Mesh Backdrop */
    .stApp {
        background: radial-gradient(circle at 10% 10%, rgba(220, 38, 38, 0.05) 0%, transparent 45%),
                    radial-gradient(circle at 90% 90%, rgba(239, 68, 68, 0.04) 0%, transparent 45%),
                    #F8FAFC !important;
        background-attachment: fixed !important;
    }

    /* Elevated White Cards */
    [data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.04) !important;
    }

    /* Custom Crimson Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #64748B;
        font-weight: 500;
        padding: 6px 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "network" not in st.session_state:
    st.session_state.network = create_default_pipeline()

if "scenario_mgr" not in st.session_state:
    st.session_state.scenario_mgr = ScenarioManager()

net: SupplyChainNetwork = st.session_state.network
scenario_mgr: ScenarioManager = st.session_state.scenario_mgr

# --- HEADER SECTION ---
st.title("Supply Chain Digital Twin")
st.caption("Discrete-Event Simulation, Stress Testing & Multi-Echelon AI Optimization")
st.divider()

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.header("Saved Scenarios")
    if scenario_mgr.scenarios:
        for sc_name in list(scenario_mgr.scenarios.keys()):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{sc_name}**")
                if col2.button("✕", key=f"del_{sc_name}"):
                    scenario_mgr.remove_scenario(sc_name)
                    st.rerun()
        if st.button("Clear All", use_container_width=True):
            scenario_mgr.clear_all()
            st.rerun()
    else:
        st.info("No saved scenarios.")

# --- NAVIGATION TABS ---
tab_net, tab_demand, tab_inv, tab_sim, tab_disrupt, tab_kpi, tab_rl, tab_compare = st.tabs([
    "Network",
    "Demand",
    "Inventory",
    "Simulation",
    "Stress-Test",
    "Financials",
    "MEIO & RL",
    "Comparison"
])

# ------------------------------------------------------------------------------
# TAB 1: NETWORK TOPOLOGY
# ------------------------------------------------------------------------------
with tab_net:
    col_map, col_stats = st.columns([2.5, 1])
    
    with col_map:
        with st.container(border=True):
            st.subheader("Pipeline Topology Map")
            fig = render_network_graph(net)
            fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
            
    with col_stats:
        with st.container(border=True):
            st.subheader("Network Nodes")
            for n_type, count in net.get_network_summary().items():
                st.metric(label=n_type.replace("_", " ").title(), value=count)

# ------------------------------------------------------------------------------
# TAB 2: DEMAND ENGINE
# ------------------------------------------------------------------------------
with tab_demand:
    with st.container(border=True):
        st.subheader("Demand Forecast Generator")
        c1, c2 = st.columns(2)
        
        with c1:
            pattern_str = st.selectbox(
                "Demand Pattern",
                [p.value for p in DemandPattern if p != DemandPattern.CUSTOM_CSV] + ["CUSTOM_CSV_UPLOAD"]
            )
            horizon_demand = st.slider("Horizon (Days)", 14, 365, 90, key="d_horizon")
            mean_d = st.number_input("Mean Daily Demand", value=500.0, step=50.0)

        with c2:
            std_d = st.number_input("Standard Deviation", value=50.0, step=10.0)
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            st.download_button(
                "Sample CSV",
                data=DataIOEngine.generate_sample_demand_csv(),
                file_name="sample_demand.csv",
                mime="text/csv"
            )

        if st.button("Generate Demand", type="primary"):
            if pattern_str == "CUSTOM_CSV_UPLOAD" and uploaded_file is not None:
                demand_series = DataIOEngine.parse_demand_csv(uploaded_file)
                horizon_demand = len(demand_series)
            else:
                config = DemandConfig(pattern=DemandPattern(pattern_str), mean_demand=mean_d, std_dev=std_d)
                demand_series = DemandEngine(config).generate_demand(horizon_demand)

            df_demand = pd.DataFrame({"Day": np.arange(1, horizon_demand + 1), "Demand": demand_series})
            fig_d = px.line(df_demand, x="Day", y="Demand", title="Demand Trajectory", color_discrete_sequence=["#DC2626"])
            fig_d.update_layout(template="plotly_white")
            st.plotly_chart(fig_d, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: INVENTORY DYNAMICS
# ------------------------------------------------------------------------------
with tab_inv:
    with st.container(border=True):
        st.subheader("Inventory Policy & Safety Stock")
        c1, c2 = st.columns(2)
        with c1:
            service_level = st.slider("Service Level (%)", 80.0, 99.9, 95.0, step=0.5) / 100.0
            lead_time = st.number_input("Lead Time (Days)", value=7, min_value=1)
            lead_time_std = st.number_input("Lead Time Std Dev", value=1.5, min_value=0.0)
        with c2:
            daily_demand_mean = st.number_input("Avg Demand", value=500.0, key="inv_mean")
            daily_demand_std = st.number_input("Demand Std Dev", value=50.0, key="inv_std")
            policy_type_str = st.selectbox("Policy Type", [p.value for p in PolicyType])

        if st.button("Calculate Policy", type="primary"):
            calc = SafetyStockCalculator()
            safety_stock = calc.calculate_safety_stock(service_level, daily_demand_mean, daily_demand_std, float(lead_time), lead_time_std)
            rop = (daily_demand_mean * lead_time) + safety_stock

            m1, m2, m3 = st.columns(3)
            m1.metric("Safety Stock", f"{int(safety_stock):,} units")
            m2.metric("Reorder Point (ROP)", f"{int(rop):,} units")
            m3.metric("Target Service Level", f"{service_level * 100:.1f}%")

# ------------------------------------------------------------------------------
# TAB 4: SIMULATION ENGINE
# ------------------------------------------------------------------------------
with tab_sim:
    with st.container(border=True):
        st.subheader("Discrete-Event Simulation")
        c1, c2 = st.columns(2)
        with c1:
            horizon_sim = st.slider("Horizon (Days)", 14, 180, 60, key="sim_horizon")
            scenario_label = st.text_input("Scenario Name", value="Baseline_Run")
        with c2:
            mean_demand_sim = st.number_input("Mean Daily Demand", value=500.0, key="sim_mean")
            std_dev_sim = st.number_input("Demand Noise", value=50.0, key="sim_std")

        if st.button("Run Simulation", type="primary"):
            d_config = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=mean_demand_sim, std_dev=std_dev_sim)
            d_engine = DemandEngine(d_config)

            sim = SupplyChainSimulation(network=net, demand_engine=d_engine, horizon_days=horizon_sim)
            sim_state = sim.run()
            df_res = sim_state.to_dataframe()

            cost_eng = CostEngine()
            costs = cost_eng.compute_costs(df_res)
            resilience = ResilienceEngine.calculate_metrics(df_res)

            scenario_mgr.add_scenario(
                name=scenario_label,
                df=df_res,
                total_cost=costs.total_operating_cost,
                fill_rate_pct=resilience.service_level_pct,
                description=f"{horizon_sim}-Day Simulation"
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Cost", f"${costs.total_operating_cost:,.2f}")
            m2.metric("OTIF Fill Rate", f"{resilience.service_level_pct:.1f}%")
            m3.metric("Peak Backlog", f"{resilience.peak_backlog:,.0f} units")

            fig_inv = px.line(df_res, x="day", y="inventory", color="node_id", title="Inventory Trajectory")
            fig_inv.update_layout(template="plotly_white")
            st.plotly_chart(fig_inv, use_container_width=True)

            st.download_button(
                "Export Results CSV",
                data=DataIOEngine.export_simulation_to_csv(df_res),
                file_name=f"{scenario_label}_results.csv",
                mime="text/csv"
            )

# ------------------------------------------------------------------------------
# TAB 5: DISRUPTION STRESS-TEST
# ------------------------------------------------------------------------------
with tab_disrupt:
    with st.container(border=True):
        st.subheader("Disruption Stress-Test")
        c1, c2 = st.columns(2)
        with c1:
            target_node = st.selectbox("Target Node", list(net.graph.nodes))
            dis_type = st.selectbox("Disruption Type", [dt.value for dt in DisruptionType])
            sim_days_dis = st.slider("Duration (Days)", 14, 180, 60, key="dis_horizon")
            dis_sc_name = st.text_input("Saved Run Name", value="Factory_Shutdown")

        with c2:
            start_day = st.number_input("Start Day", min_value=1, max_value=sim_days_dis, value=10)
            duration_days = st.number_input("Disruption Length (Days)", min_value=1, max_value=sim_days_dis, value=15)
            magnitude = st.slider("Capacity Remaining", 0.0, 1.0, 0.0)

        if st.button("Run Stress Test", type="primary"):
            d_config = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=500.0)
            d_engine = DemandEngine(d_config)

            disruption = Disruption("DIS_01", DisruptionType(dis_type), target_node, int(start_day), int(duration_days), magnitude)
            dis_engine = DisruptionEngine([disruption])

            net_disrupt = create_default_pipeline()
            sim_disrupt = SupplyChainSimulation(net_disrupt, d_engine, disruption_engine=dis_engine, horizon_days=sim_days_dis)
            df_dis = sim_disrupt.run().to_dataframe()

            costs = CostEngine().compute_costs(df_dis)
            resilience = ResilienceEngine.calculate_metrics(df_dis, disruption_start_day=int(start_day))

            scenario_mgr.add_scenario(dis_sc_name, df_dis, costs.total_operating_cost, resilience.service_level_pct, f"{dis_type} on {target_node}")
            st.success(f"Run saved as '{dis_sc_name}'.")

            fig_comp = px.line(df_dis, x="day", y="inventory", color="node_id", title="Disrupted Inventory Curve")
            fig_comp.update_layout(template="plotly_white")
            st.plotly_chart(fig_comp, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 6: FINANCIALS
# ------------------------------------------------------------------------------
with tab_kpi:
    with st.container(border=True):
        st.subheader("Financial & Cost Audit")
        h_cost = st.number_input("Holding Cost ($/unit/day)", value=0.50, step=0.10)
        b_penalty = st.number_input("Backlog Penalty ($/unit/day)", value=2.50, step=0.50)

        if st.button("Run Cost Audit", type="primary"):
            d_config = DemandConfig(pattern=DemandPattern.CONSTANT, mean_demand=500.0)
            d_engine = DemandEngine(d_config)
            sim_base = SupplyChainSimulation(network=net, demand_engine=d_engine, horizon_days=60)
            df_base = sim_base.run().to_dataframe()

            costs = CostEngine(CostParameters(h_cost, b_penalty)).compute_costs(df_base)
            st.metric("Total Operating Expense", f"${costs.total_operating_cost:,.2f}")

# ------------------------------------------------------------------------------
# TAB 7: MEIO & RL
# ------------------------------------------------------------------------------
with tab_rl:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("Multi-Echelon Optimization")
            if st.button("Compute MEIO", type="primary"):
                stages = {
                    "FAC_01": EchelonStageConfig("FAC_01", 1, 5.0, []),
                    "WH_01": EchelonStageConfig("WH_01", 2, 3.0, ["FAC_01"]),
                    "DC_01": EchelonStageConfig("DC_01", 3, 2.0, ["WH_01"]),
                }
                res = MultiEchelonOptimizer(stages).optimize_multi_echelon_safety_stock()
                st.dataframe(pd.DataFrame.from_dict(res, orient="index"), use_container_width=True)

    with c2:
        with st.container(border=True):
            st.subheader("Reinforcement Learning Agent")
            if st.button("Train RL Agent", type="primary"):
                env = SupplyChainInventoryEnv(horizon_days=30)
                agent = QLearningInventoryAgent(action_size=5)
                rewards = []
                for ep in range(50):
                    obs = env.reset()
                    tot_r = 0.0
                    done = False
                    while not done:
                        act = agent.select_action(obs)
                        n_obs, r, done, _ = env.step(act)
                        agent.learn(obs, act, r, n_obs, done)
                        obs = n_obs
                        tot_r += r
                    rewards.append(tot_r)
                st.success("Training Complete!")
                fig = px.line(
                    pd.DataFrame({"Episode": np.arange(1, 51), "Reward": rewards}),
                    x="Episode", y="Reward", title="Reward Curve",
                    color_discrete_sequence=["#DC2626"]
                )
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 8: COMPARISON
# ------------------------------------------------------------------------------
with tab_compare:
    with st.container(border=True):
        st.subheader("What-If Scenario Comparison")
        if not scenario_mgr.scenarios:
            st.info("No saved scenarios. Run simulations in Tab 4 or 5 and save them.")
        else:
            st.dataframe(scenario_mgr.get_summary_table(), use_container_width=True)
            combined_df = scenario_mgr.get_combined_dataframe()

            fig_overlay = px.line(combined_df, x="day", y="inventory", color="node_id", line_dash="Scenario", title="Multi-Scenario Overlay")
            fig_overlay.update_layout(template="plotly_white")
            st.plotly_chart(fig_overlay, use_container_width=True)