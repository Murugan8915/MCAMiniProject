from fastapi import APIRouter, Depends, status, HTTPException
from models import JobModel, PyObjectId
from database import get_database
from auth import require_role
from typing import List
from bson import ObjectId
from kafka_producer import produce_message

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobModel, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobModel, db=Depends(get_database), user: dict = Depends(require_role(["HR"]))):
    job.created_by = user["email"]
    new_job = await db["jobs"].insert_one(job.model_dump(by_alias=True, exclude={"id"}))
    created_job = await db["jobs"].find_one({"_id": new_job.inserted_id})
    return created_job

@router.get("/", response_model=List[JobModel])
async def list_jobs(db=Depends(get_database)):
    jobs = await db["jobs"].find().to_list(100)
    return jobs

@router.get("/{job_id}", response_model=JobModel)
async def get_job(job_id: str, db=Depends(get_database)):
    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobModel)
async def update_job(job_id: str, job_update: JobModel, db=Depends(get_database), user: dict = Depends(require_role(["HR"]))):
    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["created_by"] != user["email"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this job")
    
    update_data = job_update.model_dump(by_alias=True, exclude={"id", "created_by"})
    
    # Check if job is being closed/locked
    previous_status = job.get("status")
    new_status = update_data.get("status")
    
    await db["jobs"].update_one({"_id": ObjectId(job_id)}, {"$set": update_data})
    
    if new_status in ["Locked", "Closed"] and previous_status == "Active":
        # Send all relevant applications to Kafka for AI scoring
        # We include 'AI_Shortlisting' and 'AI_Error' to retry any that were stuck
        all_apps = await db["applications"].find({
            "job_id": job_id, 
            "status": {"$in": ["Applied", "AI_Shortlisting", "AI_Error"]}
        }).to_list(1000)
        
        for app in all_apps:
            # Update status to AI_Shortlisting
            await db["applications"].update_one(
                {"_id": app["_id"]},
                {"$set": {"status": "AI_Shortlisting"}}
            )
            # Send message to Kafka
            produce_message(
                topic="resume-processing",
                key=str(app["_id"]),
                value={
                    "application_id": str(app["_id"]),
                    "job_id": job_id,
                    "resume_file_id": app.get("resume_file_id"),
                    "candidate_email": app.get("candidate_email")
                }
            )

    updated_job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    return updated_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, db=Depends(get_database), user: dict = Depends(require_role(["HR"]))):
    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["created_by"] != user["email"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")
    
    await db["jobs"].delete_one({"_id": ObjectId(job_id)})
    return None
