# 📦 Supply Chain Digital Twin

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![SimPy](https://img.shields.io/badge/SimPy-4.1%2B-green.svg)](https://simpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end **Supply Chain Digital Twin** built in Python. This platform integrates discrete-event simulation (DES), multi-echelon inventory optimization (MEIO), shock propagation, financial cost modeling, and Reinforcement Learning (RL) into an executive-grade Streamlit web control center.

---

## 🌟 Key Features

* **🌐 Network Topology Engine**: Multi-stage directed graph modeling (Suppliers $\rightarrow$ Factories $\rightarrow$ Warehouses $\rightarrow$ Distribution Centers $\rightarrow$ Customers) built with `networkx` and Plotly interactive rendering.
* **📈 Stochastic Demand Generator**: Generates demand trajectories across standard statistical models (Constant, Gaussian Noise, Seasonality, Trend) and supports custom CSV file ingestion.
* **📦 Multi-Echelon Inventory Dynamics**: Standardized Safety Stock and Reorder Point (ROP) calculators implementing continuous review $(s, Q)$ and periodic review $(R, S)$ policies alongside Multi-Echelon Guaranteed Service Models (GSM).
* **⚡ Discrete-Event Simulation (DES)**: Event-driven simulation clock built on `SimPy` tracking inventory levels, order backlogs, and shipment movements day-by-day.
* **🔥 Shock Propagation & Disruption Engine**: Simulates capacity bottlenecks, facility shutdowns, and demand spikes with automated recovery and backlog dynamics.
* **📊 Financial Cost Analytics**: Computes total cost breakdowns (Holding Costs vs. Stockout/Backlog Penalties), OTIF (On-Time In-Full) fill rates, and Time-To-Recovery (TTR) metrics.
* **🤖 Reinforcement Learning (RL)**: Gym-style environment (`SupplyChainInventoryEnv`) paired with a Tabular Q-Learning agent to automate dynamic order policy learning.
* **⚖️ What-If Scenario Sandbox**: Compare multiple baseline, disrupted, and mitigated run trajectories side-by-side with CSV report exports.

---

## 📁 Repository Structure

```text
Supply-Chain-Digital-Twin/
├── .streamlit/
│   └── config.toml           # Native Crimson & Slate UI configuration
├── src/
│   ├── network.py            # Graph topology and node definition
│   ├── demand.py             # Demand pattern generation engine
│   ├── inventory.py          # Safety stock & policy engines
│   ├── simulation/           # Discrete-event engine (SimPy driven)
│   │   ├── engine.py
│   │   ├── entities.py
│   │   ├── events.py
│   │   └── state.py
│   ├── disruptions.py        # Shock injection & capacity engine
│   ├── analytics/            # Financial cost & resilience KPI engine
│   │   ├── cost.py
│   │   └── kpi.py
│   ├── optimization/         # Multi-Echelon Inventory Optimization (MEIO)
│   │   └── multi_echelon.py
│   ├── rl/                   # Gym Environment & Q-Learning agent
│   │   ├── inventory_env.py
│   │   └── agent.py
│   ├── data_io.py            # CSV Ingestion & Report Exporter
│   ├── scenario.py          # Multi-scenario manager
│   └── visualization.py      # Plotly graph visualization
├── tests/                    # Pytest test suite (20 unit tests)
├── app.py                    # Streamlit Control Center application
├── requirements.txt          # Python dependencies
└── README.md                 # Project Documentation