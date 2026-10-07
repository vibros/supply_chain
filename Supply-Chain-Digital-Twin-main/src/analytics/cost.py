"""
Financial Cost Engine for Supply Chain Performance Evaluation.
Computes holding costs, backlog/penalty costs, and gross operating expenditures.
"""

from dataclasses import dataclass
import pandas as pd


@dataclass
class CostParameters:
    holding_cost_per_unit_day: float = 0.50     # Storage cost per unit per day
    backlog_penalty_per_unit_day: float = 2.50  # Stockout/penalty cost per unit per day
    fixed_order_cost: float = 100.0             # Fixed processing cost per replenishment order


@dataclass
class CostBreakdown:
    total_holding_cost: float
    total_backlog_cost: float
    total_operating_cost: float


class CostEngine:
    def __init__(self, params: CostParameters = None):
        self.params = params or CostParameters()

    def compute_costs(self, df_snapshots: pd.DataFrame) -> CostBreakdown:
        if df_snapshots.empty:
            return CostBreakdown(0.0, 0.0, 0.0)

        # Total holding cost accumulated across all nodes & days
        total_holding = (df_snapshots["inventory"] * self.params.holding_cost_per_unit_day).sum()

        # Total backlog penalty cost accumulated across customers & days
        total_backlog = (df_snapshots["backlog"] * self.params.backlog_penalty_per_unit_day).sum()

        total_operating = total_holding + total_backlog

        return CostBreakdown(
            total_holding_cost=round(float(total_holding), 2),
            total_backlog_cost=round(float(total_backlog), 2),
            total_operating_cost=round(float(total_operating), 2),
        )