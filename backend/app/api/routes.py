from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
async def home():
    return {"message": "Hello World"}
