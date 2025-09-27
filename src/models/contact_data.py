"""
Contact data models for form filling.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ContactData:
    """Contact information for form filling"""
    first_name: str
    last_name: str
    email: str
    phone: str
    preferred_vehicles: Optional[List[str]] = None
    max_monthly_payment: Optional[float] = None
    down_payment_budget: Optional[float] = None
    additional_notes: Optional[str] = None