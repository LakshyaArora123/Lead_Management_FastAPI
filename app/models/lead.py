from __future__ import annotations
from typing import Optional
import uuid
import aiosqlite

async def create_lead(db: aiosqlite.Connection, data: dict) -> dict:
    lead_id=str(uuid.uuid4())
    await db.execute(
    	"""
        INSERT INTO leads (id, name, email, company, phone, source, notes)
        VALUES (:id, :name, :email, :company, :phone, :source, :notes)
        """,
        {
            "id": lead_id,
            "name": data["name"],
            "email": data["email"],
            "company": data.get("company"),
            "phone": data.get("phone"),
            "source": data.get("source"),
            "notes": data.get("notes"),
        },
    )
    await db.commit()
    return await get_lead_by_id(db, lead_id)

async def get_lead_by_id(db: aiosqlite.Connection, lead_id: str) -> dict | None:
    async with db.execute(
        "SELECT * FROM leads WHERE id = ?", (lead_id,)
    ) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None
    

async def get_all_leads(
    db: aiosqlite.Connection,
    *,
    status: Optional[str] = None,
    sort: str = "created_at",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    SORTABLE = {"created_at", "updated_at", "name", "status"}
    safe_sort = sort if sort in SORTABLE else "created_at"
    safe_order = "ASC" if order.lower() == "asc" else "DESC"

    where = "WHERE status = :status" if status else ""
    params: dict = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status

    async with db.execute(
        f"SELECT COUNT(*) FROM leads {where}", params
    ) as cur:
        row = await cur.fetchone()
        total = row[0]

    async with db.execute(
        f"""
        SELECT * FROM leads {where}
        ORDER BY {safe_sort} {safe_order}
        LIMIT :limit OFFSET :offset
        """,
        params,
    ) as cur:
        rows = await cur.fetchall()

    return [dict(r) for r in rows], total

async def update_lead_status(
    db: aiosqlite.Connection,
    lead_id: str,
    status: str,
    notes: Optional[str] = None,
) -> dict | None:
    if notes is not None:
        await db.execute(
            "UPDATE leads SET status = ?, notes = ? WHERE id = ?",
            (status, notes, lead_id),
        )
    else:
        await db.execute(
            "UPDATE leads SET status = ? WHERE id = ?",
            (status, lead_id),
        )

    if db.total_changes == 0:
        return None

    await db.commit()
    return await get_lead_by_id(db, lead_id)
