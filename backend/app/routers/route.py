from fastapi import APIRouter, HTTPException
import logging

from services.recognition import FaceEngine
from services.database import Database
from config import database_settings as set
from models.person import Person

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def home() -> dict:
    """Return home endpoint greeting message.

    Returns:
        dict: A dictionary containing a greeting message.

    """
    return {"message": "Hello World"}
