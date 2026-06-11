from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_matches() -> dict:
    return {"matches": [], "message": "Not implemented yet"}
