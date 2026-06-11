from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_history():
    return {"history": [], "message": "Not implemented yet"}
