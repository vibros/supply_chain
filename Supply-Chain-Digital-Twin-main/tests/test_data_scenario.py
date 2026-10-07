"""
Unit tests for CSV Data I/O and Scenario Comparison Engine.
"""

import pytest
import io
import pandas as pd

from src.data_io import DataIOEngine
from src.scenario import ScenarioManager


def test_sample_demand_csv_generation():
    csv_str = DataIOEngine.generate_sample_demand_csv()
    df = pd.read_csv(io.StringIO(csv_str))

    assert "day" in df.columns
    assert "demand" in df.columns
    assert len(df) == 90


def test_scenario_manager_aggregation():
    mgr = ScenarioManager()

    df1 = pd.DataFrame([{"day": 1, "inventory": 100.0, "node_id": "DC_01"}])
    df2 = pd.DataFrame([{"day": 1, "inventory": 200.0, "node_id": "DC_01"}])

    mgr.add_scenario("Baseline", df1, total_cost=1000.0, fill_rate_pct=98.0)
    mgr.add_scenario("Mitigated", df2, total_cost=800.0, fill_rate_pct=99.5)

    combined = mgr.get_combined_dataframe()
    assert len(combined) == 2
    assert "Scenario" in combined.columns

    summary = mgr.get_summary_table()
    assert len(summary) == 2
    assert "Total Cost ($)" in summary.columns