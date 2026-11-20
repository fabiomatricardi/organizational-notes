"""
Log entries API router.
"""
from fastapi import APIRouter, HTTPException, Query
from backend.models import LogEntryCreate, LogEntryUpdate
from backend.services import entries

router = APIRouter(prefix="/api/entries", tags=["entries"])


@router.get("")
async def list_entries(
    type: str = Query(None, description="Filter by type: LOG, TODO, TASK"),
    status: str = Query(None, description="Filter by status"),
    search: str = Query(None, description="Search in activity text"),
    owner: str = Query(None, description="Filter by owner"),
    area: str = Query(None, description="Filter by area (AIR, FIR, QIR, ICSS, PTW...)"),
    open_only: bool = Query(False, description="Only TODO/TASK not completed"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    result = await entries.get_all_entries(
        entry_type=type,
        status=status,
        search=search,
        owner=owner,
        area=area,
        open_only=open_only,
        limit=limit,
        offset=offset
    )
    return {"entries": result, "total": len(result)}


@router.get("/follow-up")
async def get_follow_up():
    """Open commitments grouped by owner, with overdue / stale / orphan flags."""
    return await entries.get_follow_up()


@router.get("/today")
async def get_today():
    """Today's entries + everything due, stale or overdue."""
    return await entries.get_today()


@router.get("/stats/dashboard")
async def get_dashboard_stats():
    return await entries.get_dashboard_stats()


@router.get("/{entry_id}")
async def get_entry(entry_id: int):
    result = await entries.get_entry(entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result


@router.post("")
async def create_entry(entry: LogEntryCreate):
    try:
        result = await entries.create_entry(entry.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}")
async def update_entry(entry_id: int, entry: LogEntryUpdate):
    result = await entries.update_entry(entry_id, entry.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result


@router.delete("/{entry_id}")
async def delete_entry(entry_id: int):
    success = await entries.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}
