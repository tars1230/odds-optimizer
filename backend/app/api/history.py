from fastapi import APIRouter
from app.database import get_bet_history

router = APIRouter()


@router.get("/")
async def get_history(limit: int = 50) -> dict:
    """Get bet history."""
    history = await get_bet_history(limit)
    return {"history": history, "count": len(history)}
