# Returns profile info of logged-in user

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models.recipe import User


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    returns profile info of logged-in user
    """

    user = db.query(User).filter(User.id == user_id).first()
    
    return {"id": user.id, "name": user.name, "email": user.email, 
            "dietary_restrictions": user.dietary_restrictions, "allergens": user.allergens}