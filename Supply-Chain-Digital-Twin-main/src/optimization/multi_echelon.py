"""
Multi-Echelon Inventory Optimization (MEIO) Engine.
Calculates net lead times and optimized safety stock across linked echelons.
"""

from dataclasses import dataclass
from typing import Dict, List
import scipy.stats as stats
import numpy as np


@dataclass
class EchelonStageConfig:
    node_id: str
    echelon_level: int              # 1: Factory, 2: Warehouse, 3: DC, 4: Retailer
    nominal_lead_time: float         # Days required to process/transport locally
    inbound_stage_ids: List[str]    # Direct upstream parent node IDs
    service_level: float = 0.95
    daily_demand_std: float = 50.0


class MultiEchelonOptimizer:
    def __init__(self, stage_configs: Dict[str, EchelonStageConfig]):
        self.stages = stage_configs

    def calculate_guaranteed_service_times(self) -> Dict[str, float]:
        """
        Computes incoming service times and net processing times across echelons.
        Net Lead Time = Local Processing Lead Time + Upstream Service Time Delay.
        """
        net_lead_times: Dict[str, float] = {}

        # Sort stages by echelon level ascending (Upstream -> Downstream)
        sorted_stages = sorted(self.stages.values(), key=lambda s: s.echelon_level)

        for stage in sorted_stages:
            if not stage.inbound_stage_ids:
                max_upstream_delay = 0.0
            else:
                max_upstream_delay = max(
                    net_lead_times.get(up_id, 0.0) for up_id in stage.inbound_stage_ids
                )

            net_lead_times[stage.node_id] = stage.nominal_lead_time + max_upstream_delay

        return net_lead_times

    def optimize_multi_echelon_safety_stock(self) -> Dict[str, Dict[str, float]]:
        """
        Calculates single-echelon vs multi-echelon safety stock allocations.
        """
        net_lead_times = self.calculate_guaranteed_service_times()
        results: Dict[str, Dict[str, float]] = {}

        for node_id, stage in self.stages.items():
            z_score = stats.norm.ppf(stage.service_level)
            
            single_echelon_ss = z_score * stage.daily_demand_std * np.sqrt(stage.nominal_lead_time)

            net_lt = net_lead_times[node_id]
            multi_echelon_ss = z_score * stage.daily_demand_std * np.sqrt(net_lt)

            results[node_id] = {
                "nominal_lead_time": stage.nominal_lead_time,
                "net_lead_time": round(net_lt, 2),
                "single_echelon_safety_stock": round(float(single_echelon_ss), 2),
                "multi_echelon_safety_stock": round(float(multi_echelon_ss), 2),
                "buffer_delta": round(float(multi_echelon_ss - single_echelon_ss), 2),
            }

        return results