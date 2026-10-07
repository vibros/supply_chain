"""
Demand Generation Engine for Supply Chain Digital Twin.
Supports deterministic, Gaussian noise, seasonality, trend, and CSV inputs.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import numpy as np
import pandas as pd


class DemandPattern(Enum):
    CONSTANT = "CONSTANT"
    RANDOM_NORMAL = "RANDOM_NORMAL"
    SEASONAL = "SEASONAL"
    TREND_AND_NOISE = "TREND_AND_NOISE"
    CUSTOM_CSV = "CUSTOM_CSV"


@dataclass
class DemandConfig:
    pattern: DemandPattern = DemandPattern.CONSTANT
    mean_demand: float = 100.0
    std_dev: float = 15.0
    seasonality_period: int = 7  # e.g., weekly cycles
    seasonality_amplitude: float = 20.0
    trend_slope: float = 0.5     # Units increase per day
    seed: Optional[int] = 42


class DemandEngine:
    def __init__(self, config: DemandConfig):
        self.config = config

    def generate_demand(self, horizon_days: int, csv_filepath: Optional[str] = None) -> np.ndarray:
        """
        Generates daily demand array for a given simulation horizon.
        """
        if horizon_days <= 0:
            raise ValueError("horizon_days must be greater than 0.")

        if self.config.seed is not None:
            np.random.seed(self.config.seed)

        if self.config.pattern == DemandPattern.CONSTANT:
            demand = np.full(horizon_days, fill_value=self.config.mean_demand, dtype=float)

        elif self.config.pattern == DemandPattern.RANDOM_NORMAL:
            demand = np.random.normal(
                loc=self.config.mean_demand,
                scale=self.config.std_dev,
                size=horizon_days,
            )

        elif self.config.pattern == DemandPattern.SEASONAL:
            days = np.arange(horizon_days)
            seasonal_component = self.config.seasonality_amplitude * np.sin(
                2 * np.pi * days / self.config.seasonality_period
            )
            noise = np.random.normal(0, self.config.std_dev, size=horizon_days)
            demand = self.config.mean_demand + seasonal_component + noise

        elif self.config.pattern == DemandPattern.TREND_AND_NOISE:
            days = np.arange(horizon_days)
            trend_component = self.config.trend_slope * days
            noise = np.random.normal(0, self.config.std_dev, size=horizon_days)
            demand = self.config.mean_demand + trend_component + noise

        elif self.config.pattern == DemandPattern.CUSTOM_CSV:
            if not csv_filepath:
                raise ValueError("csv_filepath must be provided for CUSTOM_CSV pattern.")
            df = pd.read_csv(csv_filepath)
            if "demand" not in df.columns:
                raise KeyError("CSV file must contain a 'demand' column.")
            demand_vals = df["demand"].values[:horizon_days]
            if len(demand_vals) < horizon_days:
                # Pad with last known value if horizon is longer than CSV rows
                padding = np.full(horizon_days - len(demand_vals), demand_vals[-1])
                demand = np.concatenate([demand_vals, padding])
            else:
                demand = demand_vals

        else:
            raise NotImplementedError(f"Demand pattern {self.config.pattern} not implemented.")

        # Real-world constraint: Demand cannot be negative
        return np.clip(demand, a_min=0.0, a_max=None)