from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models.core import User

router = APIRouter()

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name,
        "timezone": current_user.timezone,
        "onboarding_completed": current_user.onboarding_completed
    }
