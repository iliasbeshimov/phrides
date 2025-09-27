"""
Core data models for contact requests and user information.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class UserInfo:
    """User information for contact forms"""
    first_name: str
    last_name: str
    email: str
    phone: str
    preferred_contact_method: str = "email"


@dataclass 
class ContactRequest:
    """Complete contact request with user info and preferences"""
    user_info: UserInfo
    custom_message: str
    vehicle_preferences: List[str]
    project_id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class DealershipInfo:
    """Dealership information"""
    id: str
    name: str
    website: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None