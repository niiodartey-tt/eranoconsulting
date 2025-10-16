from fastapi import APIRouter, Depends
from app.utils import get_current_user
from app.models import User

router = APIRouter(prefix="/protected", tags=["Protected"])


@router.get("/")
async def protected_route(current_user=Depends(get_current_user)):
    # Use getattr with fallback to handle different attribute names
    name = (
        getattr(current_user, "full_name", None)
        or getattr(current_user, "name", None)
        or getattr(current_user, "username", None)
        or current_user.email.split("@")[0]
    )

    return {
        "message": f"Hello {current_user.email}, you have accessed a protected route!",
        "email": current_user.email,
        "role": getattr(current_user, "role", "user"),
        "user_id": current_user.id,
    }


@router.get("/some-protected-endpoint")
async def some_protected_endpoint(current_user: User = Depends(get_current_user)):
    """Another protected endpoint example"""
    name = (
        getattr(current_user, "full_name", None)
        or getattr(current_user, "name", None)
        or current_user.email
    )

    return {
        "message": "This is some protected data",
        "user": {
            "name": name,
            "email": current_user.email,
            "role": getattr(current_user, "role", "user"),
        },
        "data": {"example": "sensitive information here", "status": "success"},
    }
