import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from database import get_database, get_gridfs
from auth import require_role, get_current_user
from kafka_producer import produce_message
from datetime import datetime
from bson import ObjectId
from models import ApplicationModel

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/")
async def apply_for_job(
    job_id: str = Form(...),
    resume: UploadFile = File(...),
    db=Depends(get_database),
    fs=Depends(get_gridfs),
    user: dict = Depends(require_role(["Candidate"]))
):
    print(f"\n--- DEBUG: New Application Request Received ---")
    print(f"Step 1: Checking file type for {resume.filename}...")
    if not resume.filename.endswith(".pdf"):
        print("DEBUG: ❌ Validation Failed: Not a PDF")
        raise HTTPException(status_code=400, detail="Only PDF resumes are allowed")
    
    try:
        job_oid = ObjectId(job_id)
    except:
        print(f"DEBUG: ❌ Validation Failed: Invalid job ID format '{job_id}'")
        raise HTTPException(status_code=400, detail="Invalid job ID format")
        
    print(f"Step 2: Verifying Job {job_id} exists and is Active...")
    job = await db["jobs"].find_one({"_id": job_oid})
    if not job:
        print("DEBUG: ❌ Error: Job not found in database")
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.get("status") != "Active":
        print(f"DEBUG: ❌ Error: Job status is {job.get('status')}, cannot apply")
        raise HTTPException(status_code=400, detail="This job is currently inactive or locked")
    
    print("Step 3: Saving PDF to MongoDB GridFS...")
    # Store in GridFS
    file_id = await fs.upload_from_stream(
        resume.filename,
        await resume.read(),
        metadata={"contentType": resume.content_type}
    )
    print(f"DEBUG: ✅ PDF saved successfully with GridFS ID: {file_id}")

    print("Step 4: Preparing Application document...")
    application = {
        "job_id": job_id,
        "candidate_name": user["name"],
        "candidate_email": user["email"],
        "candidate_mobile": user.get("mobile_number", "N/A"),
        "resume_file_id": str(file_id),
        "status": "Applied",
        "applied_at": datetime.utcnow()
    }
    print(f"DEBUG: Document data: {application}")
    
    print("Step 5: Inserting Application into 'applications' collection...")
    result = await db["applications"].insert_one(application)
    application_id = str(result.inserted_id)
    print(f"DEBUG: ✅ Application saved successfully with DB ID: {application_id}")

    print("--- DEBUG: Application Process Complete ---\n")
        
    return {"message": "Application submitted successfully", "application_id": application_id, "resume_file_id": str(file_id)}

@router.put("/{app_id}/status")
async def update_application_status(
    app_id: str, 
    status: str = Form(...), 
    db=Depends(get_database), 
    user: dict = Depends(get_current_user)
):
    try:
        app_oid = ObjectId(app_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid application ID format")

    # Security Check: Candidates can only update their own status to specific states
    if user["role"] == "Candidate":
        existing_app = await db["applications"].find_one({"_id": app_oid})
        if not existing_app:
            raise HTTPException(status_code=404, detail="Application not found")
        if existing_app.get("candidate_email", "").strip().lower() != user.get("email", "").strip().lower():
            raise HTTPException(status_code=403, detail="You can only update your own application")
        if status not in ["Exam Finished", "Document Uploaded"]:
            raise HTTPException(status_code=403, detail="Invalid status transition for candidates")
    elif user["role"] not in ["HR", "Technical Panel"]:
        raise HTTPException(status_code=403, detail="Unauthorized role")
        
    app = await db["applications"].find_one({"_id": app_oid})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    result = await db["applications"].update_one(
        {"_id": app_oid},
        {"$set": {"status": status}}
    )
    
    # Trigger notification via Kafka
    job = await db["jobs"].find_one({"_id": ObjectId(app["job_id"])})
    produce_message("application_status", app_id, {
        "application_id": app_id,
        "new_status": status,
        "candidate_email": app["candidate_email"],
        "candidate_name": app.get("candidate_name", "Candidate"),
        "job_title": job.get("title", "Position") if job else "Position"
    })
        
    return {"message": f"Status updated to {status}"}
    
@router.put("/job/{job_id}/status-bulk")
async def bulk_update_status(
    job_id: str,
    from_status: str = Form(...),
    to_status: str = Form(...),
    db=Depends(get_database),
    user: dict = Depends(require_role(["HR"]))
):
    result = await db["applications"].update_many(
        {"job_id": job_id, "status": from_status},
        {"$set": {"status": to_status}}
    )
    return {"message": f"Updated {result.modified_count} applications from {from_status} to {to_status}"}

@router.get("/my-applications", response_model=list[ApplicationModel])
async def get_my_applications(db=Depends(get_database), user: dict = Depends(require_role(["Candidate"]))):
    email = user["email"].strip()
    apps = await db["applications"].find({
        "candidate_email": {"$regex": f"^{email}\\s*$", "$options": "i"}
    }).to_list(100)
    return apps

@router.get("/job/{job_id}", response_model=list[ApplicationModel])
async def get_job_applications(job_id: str, db=Depends(get_database), user: dict = Depends(require_role(["HR"]))):
    apps = await db["applications"].find({"job_id": job_id}).to_list(100)
    return apps

@router.post("/{app_id}/documents")
async def upload_document(
    app_id: str,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db=Depends(get_database),
    fs=Depends(get_gridfs),
    user: dict = Depends(get_current_user)
):
    # Store in GridFS
    file_id = await fs.upload_from_stream(
        file.filename,
        await file.read(),
        metadata={"contentType": file.content_type}
    )
    
    doc = {
        "application_id": app_id,
        "document_type": doc_type,
        "file_id": str(file_id),
        "uploaded_at": datetime.utcnow()
    }
    await db["documents"].insert_one(doc)
    return {"message": f"{doc_type} uploaded successfully", "file_id": str(file_id)}

@router.get("/{app_id}/documents")
async def get_application_documents(app_id: str, db=Depends(get_database), user: dict = Depends(get_current_user)):
    docs = await db["documents"].find({"application_id": app_id}).to_list(100)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

@router.get("/resume/{file_id}")
async def get_resume(file_id: str, fs=Depends(get_gridfs)):
    try:
        grid_out = await fs.open_download_stream(ObjectId(file_id))
        from fastapi.responses import StreamingResponse
        return StreamingResponse(grid_out, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Resume not found")
