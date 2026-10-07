"""
Resilience & Performance KPI Engine.
Computes OTIF (On-Time In-Full) service levels, Time-To-Recovery (TTR), and resilience index.
"""

from dataclasses import dataclass
import pandas as pd


@dataclass
class PerformanceMetrics:
    service_level_pct: float       # OTIF Fill Rate %
    total_requested_demand: float
    total_fulfilled_demand: float
    peak_backlog: float
    time_to_recovery_days: int     # Days required for backlog to clear after disruption
    resilience_score: float        # Index scaled 0-100


class ResilienceEngine:
    @staticmethod
    def calculate_metrics(df_snapshots: pd.DataFrame, disruption_start_day: int = 0) -> PerformanceMetrics:
        if df_snapshots.empty:
            return PerformanceMetrics(0.0, 0.0, 0.0, 0.0, 0, 0.0)

        # Filter customer records
        cust_records = df_snapshots[df_snapshots["node_id"].str.startswith("CUST")]
        
        total_req = cust_records["requested_demand"].max() if not cust_records.empty else 1.0
        total_ful = cust_records["fulfilled_demand"].max() if not cust_records.empty else 0.0

        fill_rate = (total_ful / total_req * 100.0) if total_req > 0 else 100.0
        fill_rate = min(100.0, max(0.0, fill_rate))

        peak_backlog = float(cust_records["backlog"].max()) if not cust_records.empty else 0.0

        # Calculate Time-To-Recovery (TTR)
        ttr = 0
        if disruption_start_day > 0 and not cust_records.empty:
            post_disrupt = cust_records[cust_records["day"] >= disruption_start_day]
            backlog_days = post_disrupt[post_disrupt["backlog"] > 0]["day"]
            if not backlog_days.empty:
                recovery_day = backlog_days.max()
                ttr = max(0, int(recovery_day - disruption_start_day))

        # Composite Resilience Score (100 = perfect service, zero backlog)
        backlog_penalty_factor = min(50.0, (peak_backlog / (total_req + 1e-5)) * 50.0)
        resilience_score = max(0.0, min(100.0, fill_rate - backlog_penalty_factor))

        return PerformanceMetrics(
            service_level_pct=round(fill_rate, 2),
            total_requested_demand=round(float(total_req), 2),
            total_fulfilled_demand=round(float(total_ful), 2),
            peak_backlog=round(peak_backlog, 2),
            time_to_recovery_days=ttr,
            resilience_score=round(resilience_score, 2),
        )