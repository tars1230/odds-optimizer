from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_history() -> dict:
    return {"history": [], "message": "Not implemented yet"}
