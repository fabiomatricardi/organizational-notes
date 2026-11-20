"""
Chat API router.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatSearchRequest(BaseModel):
    query: str = ""
    top_k: int = 10
    search_mode: str = "text"
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class DateSearchRequest(BaseModel):
    date_from: str
    date_to: str
    limit: int = 50


class ChatSendRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    rag_entry_ids: Optional[list[int]] = None


@router.post("/search")
async def search(request: ChatSearchRequest):
    top_k = max(5, min(40, request.top_k))
    results = await chat_service.search_entries(request.query, top_k)
    return {"results": results, "total": len(results)}


@router.post("/search-by-date")
async def search_by_date(request: DateSearchRequest):
    limit = max(1, min(200, request.limit))
    results = await chat_service.search_entries_by_date(request.date_from, request.date_to, limit)
    return {"results": results, "total": len(results)}


@router.post("/send")
async def send(request: ChatSendRequest):
    try:
        result = await chat_service.send_message(
            conversation_id=request.conversation_id,
            user_message=request.message,
            rag_entry_ids=request.rag_entry_ids,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations():
    return {"conversations": chat_service.list_conversations()}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    result = chat_service.get_conversation(conversation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    success = chat_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}
