from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class LeadStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    lost = "lost"
    converted = "converted"

class LeadCreate(BaseModel):
    name: str =Field(...,min_length=1,max_length=120)
    email: EmailStr
    company: Optional[str] = Field(None,max_length=120)
    phone: Optional[str] = Field(None,max_length=30)
    source: Optional[str] = Field(None,max_length=80)
    notes: Optional[str] = Field(None,max_length=2000)

    @field_validator("name", "company", "source", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, v):
        return v.strip().lower() if isinstance(v, str) else v

class LeadOut(BaseModel):
    id: str
    name: str
    email: str
    company: Optional[str]
    phone: Optional[str]
    source: Optional[str]
    status: LeadStatus
    notes: Optional[str]
    created_at: str
    updated_at: str
    model_config = {"from_attributes": True}

#to fetch all leads
class LeadListResponse(BaseModel):
    data: list[LeadOut]
    meta: dict

#to fetch one lead
class LeadResponse(BaseModel):
    data: LeadOut

#to update lead status
class LeadStatusUpdate(BaseModel):
    status: LeadStatus
    notes: Optional[str] = Field(None,max_length=2000)