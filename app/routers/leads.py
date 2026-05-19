from __future__ import annotations

from typing import Literal, Optional

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import IntegrityError

from app.db.database import get_db
from app.models import lead as lead_model
from app.schemas.lead import (
    LeadCreate,
    LeadListResponse,
    LeadOut,
    LeadResponse,
    LeadStatus,
    LeadStatusUpdate,
)

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.post(
    "",
    response_model=LeadResponse,
    status_code=201,
    summary="Create a new lead",
)
async def create_lead(
    body: LeadCreate,
    db: aiosqlite.Connection = Depends(get_db),
):
    try:
        lead = await lead_model.create_lead(db, body.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A lead with this email already exists.",
        )
    return {"data": lead}


@router.get(
    "",
    response_model=LeadListResponse,
    summary="Fetch all leads",
)
async def get_leads(
    status: Optional[LeadStatus] = Query(None, description="Filter by status"),
    sort: Literal["created_at", "updated_at", "name", "status"] = Query(
        "created_at", description="Field to sort by"
    ),
    order: Literal["asc", "desc"] = Query("desc", description="Sort direction"),
    limit: int = Query(50, ge=1, le=200, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: aiosqlite.Connection = Depends(get_db),
):
    leads, total = await lead_model.get_all_leads(
        db,
        status=status.value if status else None,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset,
    )
    return {
        "data": leads,
        "meta": {"total": total, "limit": limit, "offset": offset},
    }


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Fetch a single lead",
)
async def get_lead(
    lead_id: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    lead = await lead_model.get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return {"data": lead}


@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse,
    summary="Update a lead's status",
)
async def update_status(
    lead_id: str,
    body: LeadStatusUpdate,
    db: aiosqlite.Connection = Depends(get_db),
):
    lead = await lead_model.update_lead_status(
        db, lead_id, body.status.value, body.notes
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return {"data": lead}
