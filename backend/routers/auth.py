from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database import get_database
from models import UserModel
from auth_utils import verify_password, get_password_hash, create_access_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

class CandidateLoginRequest(BaseModel):
    mobile_number: str
    name: str
    email: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

@router.post("/login/candidate", response_model=LoginResponse)
async def login_candidate(request: CandidateLoginRequest, db=Depends(get_database)):
    # Simple candidate login/registration via email
    user = await db["users"].find_one({"email": request.email, "role": "Candidate"})
    if user:
        # Update user with the latest name and mobile from the login form
        await db["users"].update_one(
            {"_id": user["_id"]},
            {"$set": {"name": request.name, "mobile_number": request.mobile_number}}
        )
        user["name"] = request.name
        user["mobile_number"] = request.mobile_number
    else:
        user_obj = {
            "name": request.name,
            "email": request.email,
            "mobile_number": request.mobile_number,
            "role": "Candidate"
        }
        await db["users"].insert_one(user_obj)
        user = user_obj
    
    token = create_access_token(data={"sub": user["email"], "role": "Candidate"})
    return {"access_token": token, "token_type": "bearer", "role": "Candidate"}

@router.post("/login", response_model=LoginResponse)
async def login_staff(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_database)):
    # For HR and Technical Panel
    user = await db["users"].find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(data={"sub": user["email"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

@router.post("/register/staff")
async def register_staff(user: UserModel, db=Depends(get_database)):
    # Helper to register HR/Tech for dev
    if user.role not in ["HR", "Technical Panel"]:
        raise HTTPException(status_code=400, detail="Invalid role for staff registration")
    
    existing = await db["users"].find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_dict = user.model_dump(exclude={"id"})
    user_dict["hashed_password"] = get_password_hash("password123") # Default for dev
    await db["users"].insert_one(user_dict)
    return {"message": "Staff user registered"}
