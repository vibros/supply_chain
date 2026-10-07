"""
Scenario Manager for Storing and Comparing 'What-If' Simulation Runs.
"""

from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd


@dataclass
class ScenarioRecord:
    name: str
    dataframe: pd.DataFrame
    total_cost: float
    fill_rate_pct: float
    description: str = ""


class ScenarioManager:
    def __init__(self):
        self.scenarios: Dict[str, ScenarioRecord] = {}

    def add_scenario(self, name: str, df: pd.DataFrame, total_cost: float = 0.0, fill_rate_pct: float = 100.0, description: str = ""):
        df_copy = df.copy()
        df_copy["Scenario"] = name
        self.scenarios[name] = ScenarioRecord(
            name=name,
            dataframe=df_copy,
            total_cost=total_cost,
            fill_rate_pct=fill_rate_pct,
            description=description
        )

    def remove_scenario(self, name: str):
        if name in self.scenarios:
            del self.scenarios[name]

    def clear_all(self):
        self.scenarios.clear()

    def get_combined_dataframe(self) -> pd.DataFrame:
        if not self.scenarios:
            return pd.DataFrame()
        return pd.concat([rec.dataframe for rec in self.scenarios.values()], ignore_index=True)

    def get_summary_table(self) -> pd.DataFrame:
        summary_rows = []
        for name, rec in self.scenarios.items():
            summary_rows.append({
                "Scenario Name": name,
                "Total Cost ($)": rec.total_cost,
                "OTIF Fill Rate (%)": rec.fill_rate_pct,
                "Description": rec.description
            })
        return pd.DataFrame(summary_rows)