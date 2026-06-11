from fastapi import APIRouter, Query
from app.database import get_bet_history

router = APIRouter()


@router.get("/")
async def get_history(limit: int = Query(default=50, ge=1, le=1000)) -> dict:
    """Get bet history."""
    history = await get_bet_history(limit)
    return {"history": history, "count": len(history)}
