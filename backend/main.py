from fastapi import FastAPI
from database import db
from routers import jobs, applications, technical, auth
from models import UserModel
from auth_utils import get_password_hash
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI(title="AI Recruitment Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    # Seed dummy users only if they don't already exist
    existing_hr = await db["users"].find_one({"username": "hr_alice"})
    if not existing_hr:
        dummy_hr = {
            "name": "Alice HR",
            "email": "hr@recruitment.com",
            "username": "hr_alice",
            "hashed_password": get_password_hash("password123"),
            "role": "HR"
        }
        dummy_tech = {
            "name": "Charlie Tech",
            "email": "tech@recruitment.com",
            "username": "tech_charlie",
            "hashed_password": get_password_hash("password123"),
            "role": "Technical Panel"
        }
        await db["users"].insert_many([dummy_hr, dummy_tech])
        print("Database seeded with dummy staff users.")
    else:
        print("Dummy users already exist — skipping seed.")

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(technical.router)

@app.get("/")
async def root():
    return {"message": "AI Recruitment Platform Backend API is running."}
