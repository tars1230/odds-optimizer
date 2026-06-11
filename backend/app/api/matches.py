from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_matches():
    return {"matches": [], "message": "Not implemented yet"}
