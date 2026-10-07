"""
Data Ingestion and Report Export Utilities.
Handles custom demand/network CSV loading and simulation data exporting.
"""

import io
import pandas as pd
from typing import List, Optional


class DataIOEngine:
    @staticmethod
    def parse_demand_csv(file_buffer) -> List[float]:
        """Reads a user-uploaded CSV file containing a 'demand' column."""
        df = pd.read_csv(file_buffer)
        if "demand" not in df.columns and "Demand" not in df.columns:
            # Fallback to the first numeric column
            numeric_cols = df.select_dtypes(include=["float", "int"]).columns
            if len(numeric_cols) == 0:
                raise ValueError("CSV must contain a numeric column for daily demand.")
            col_name = numeric_cols[0]
        else:
            col_name = "demand" if "demand" in df.columns else "Demand"

        return df[col_name].astype(float).tolist()

    @staticmethod
    def export_simulation_to_csv(df_simulation: pd.DataFrame) -> str:
        """Converts simulation snapshot dataframe into a downloadable CSV string."""
        return df_simulation.to_csv(index=False)

    @staticmethod
    def generate_sample_demand_csv() -> str:
        """Generates sample 90-day CSV content for user download/testing."""
        import numpy as np
        days = np.arange(1, 91)
        demand = np.round(500 + 50 * np.sin(days / 7) + np.random.normal(0, 30, 90), 2)
        df_sample = pd.DataFrame({"day": days, "demand": np.maximum(10.0, demand)})
        return df_sample.to_csv(index=False)