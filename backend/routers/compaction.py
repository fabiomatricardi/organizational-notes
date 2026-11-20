"""
Compaction API router - AI-powered duplicate detection and merge.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services import compaction

router = APIRouter(prefix="/api/compaction", tags=["compaction"])


class DetectRequest(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    entry_type: Optional[str] = None


class MergeRequest(BaseModel):
    primary_id: int
    secondary_ids: list[int]


@router.get("/stats")
async def stats():
    try:
        return await compaction.get_compaction_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect")
async def detect(request: DetectRequest):
    try:
        return await compaction.detect_duplicates(
            request.date_from,
            request.date_to,
            request.entry_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge")
async def merge(request: MergeRequest):
    try:
        return await compaction.merge_entries(
            request.primary_id,
            request.secondary_ids
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
