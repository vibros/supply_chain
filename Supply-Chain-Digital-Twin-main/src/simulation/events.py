"""
Event definitions and Shipment In-Transit Data Classes.
"""

from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    DEMAND_ARRIVED = "DEMAND_ARRIVED"
    ORDER_PLACED = "ORDER_PLACED"
    PRODUCTION_STARTED = "PRODUCTION_STARTED"
    SHIPMENT_DISPATCHED = "SHIPMENT_DISPATCHED"
    SHIPMENT_ARRIVED = "SHIPMENT_ARRIVED"


@dataclass
class Shipment:
    shipment_id: str
    source_id: str
    destination_id: str
    quantity: float
    dispatch_day: float
    arrival_day: float
    transit_cost: float