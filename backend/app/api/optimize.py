from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def optimize_budget() -> dict:
    return {"recommendations": [], "message": "Not implemented yet"}
