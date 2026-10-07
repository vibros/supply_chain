"""
Safety stock calculation engines.
"""

from dataclasses import dataclass
import scipy.stats as stats


@dataclass
class SafetyStockConfig:
    service_level: float = 0.95
    lead_time_days: float = 7.0
    lead_time_std: float = 1.5


class SafetyStockCalculator:
    """Calculates required safety stock using normal distribution approximation."""

    @staticmethod
    def calculate_safety_stock(
        service_level: float,
        avg_demand: float,
        std_demand: float,
        avg_lead_time: float,
        std_lead_time: float,
    ) -> float:
        z_score = stats.norm.ppf(service_level)
        variance_demand = avg_lead_time * (std_demand ** 2)
        variance_lead_time = (avg_demand ** 2) * (std_lead_time ** 2)
        safety_stock = z_score * ((variance_demand + variance_lead_time) ** 0.5)
        return float(safety_stock)

    def norm_calc(
        self,
        service_level: float,
        avg_demand: float,
        std_demand: float,
        avg_lead_time: float,
        std_lead_time: float,
    ) -> float:
        """Alias for backward compatibility."""
        return self.calculate_safety_stock(
            service_level, avg_demand, std_demand, avg_lead_time, std_lead_time
        )


# Alias for backward compatibility
CalculateSafetyStock = SafetyStockCalculator