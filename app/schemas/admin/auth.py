from pydantic import BaseModel, EmailStr, Field, validator, root_validator
import re
import socket
from typing import Optional, Dict, Any, List

class EncryptRequest(BaseModel):
    value: str = Field(..., description="The value to encrypt", min_length=1)

class DecryptRequest(BaseModel):
    value: str


class AdminLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    

class AdminRegisterRequest(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="StrongPass123!")
    mobile_number: Optional[str] = Field(None, example="9876543210")

    class Config:
        str_min_length = 1  # Enforces a minimum length for string fields
        str_strip_whitespace = True  # Strips leading/trailing whitespace from string fields


class OrganizationCreate(BaseModel):
    uuid: str
    name: str
    slug: str
    subscription_status: str = "new"


class UserCreate(BaseModel):
    uuid: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    role: str = "admin"
    level: int = 0
    points: int = 0
    is_verified: bool = False
    is_active: bool = True
    stripe_customer_id: str | None = None
    password: str = Field(..., min_length=6)
    organization: OrganizationCreate




