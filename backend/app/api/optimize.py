from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def optimize_budget():
    return {"recommendations": [], "message": "Not implemented yet"}
