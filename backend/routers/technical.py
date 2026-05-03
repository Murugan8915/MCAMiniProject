from fastapi import APIRouter, Depends, HTTPException, status
from models import QuestionModel, AnswerModel, ApplicationModel
from database import get_database
from auth import require_role, get_current_user
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/technical", tags=["Technical Panel"])

@router.post("/questions", response_model=QuestionModel)
async def create_question(question: QuestionModel, db=Depends(get_database), user: dict = Depends(require_role(["Technical Panel"]))):
    result = await db["questions"].insert_one(question.model_dump(by_alias=True, exclude={"id"}))
    created = await db["questions"].find_one({"_id": result.inserted_id})
    return created

@router.get("/questions/{job_id}", response_model=List[QuestionModel])
async def get_job_questions(job_id: str, db=Depends(get_database), user: dict = Depends(get_current_user)):
    # Both Tech Panel and Candidates need to see questions
    questions = await db["questions"].find({"job_id": job_id}).to_list(100)
    return questions

@router.post("/answers", response_model=AnswerModel)
async def submit_answer(answer: AnswerModel, db=Depends(get_database), user: dict = Depends(require_role(["Candidate"]))):
    # Verify application exists and belongs to user
    app = await db["applications"].find_one({
        "_id": ObjectId(answer.application_id), 
        "candidate_email": {"$regex": f"^{user['email'].strip()}\\s*$", "$options": "i"}
    })
    if not app:
        raise HTTPException(status_code=404, detail="Application not found or not owned by user")
    
    result = await db["answers"].insert_one(answer.model_dump(by_alias=True, exclude={"id"}))
    created = await db["answers"].find_one({"_id": result.inserted_id})
    return created

@router.post("/answers/bulk")
async def submit_answers_bulk(
    answers: List[AnswerModel], 
    db=Depends(get_database), 
    user: dict = Depends(get_current_user)
):
    if user["role"] != "Candidate":
         raise HTTPException(status_code=403, detail="Only candidates can submit answers")
    
    if not answers:
        return {"message": "No answers provided"}
    
    # Verify application exists and belongs to user
    app_id = answers[0].application_id
    app = await db["applications"].find_one({
        "_id": ObjectId(app_id), 
        "candidate_email": {"$regex": f"^{user['email'].strip()}\\s*$", "$options": "i"}
    })
    if not app:
        raise HTTPException(status_code=404, detail="Application not found or not owned by user")
    
    # Clear previous answers for this application to avoid duplicates
    await db["answers"].delete_many({"application_id": app_id})
    
    answer_docs = [a.model_dump(by_alias=True, exclude={"id"}) for a in answers]
    await db["answers"].insert_many(answer_docs)
    return {"message": f"{len(answer_docs)} answers submitted successfully"}

@router.put("/answers/{answer_id}/score")
async def score_answer(answer_id: str, score: int, feedback: str, db=Depends(get_database), user: dict = Depends(require_role(["Technical Panel"]))):
    result = await db["answers"].update_one(
        {"_id": ObjectId(answer_id)},
        {"$set": {"score": score, "feedback": feedback}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {"message": "Answer scored successfully"}

@router.get("/applications/evaluation-pending", response_model=List[ApplicationModel])
async def get_pending_evaluations(db=Depends(get_database), user: dict = Depends(require_role(["Technical Panel"]))):
    apps = await db["applications"].find({"status": {"$in": ["Exam Finished", "Technical Evaluation"]}}).to_list(100)
    return apps

@router.get("/job/{job_id}/check-hr-processing")
async def check_hr_processing(job_id: str, db=Depends(get_database), user: dict = Depends(require_role(["Technical Panel"]))):
    # Check if any candidates have been moved to technical stages
    tech_count = await db["applications"].count_documents({
        "job_id": job_id,
        "status": {"$in": ["Technical Assigned", "Exam Finished", "Technical Evaluation"]}
    })
    
    # Check if there are any shortlisted candidates still waiting
    shortlisted_count = await db["applications"].count_documents({
        "job_id": job_id,
        "status": "Shortlisted"
    })
    
    return {
        "has_tech_candidates": tech_count > 0,
        "has_shortlisted_waiting": shortlisted_count > 0
    }

@router.get("/answers/{application_id}", response_model=List[AnswerModel])
async def get_application_answers(application_id: str, db=Depends(get_database), user: dict = Depends(require_role(["Technical Panel", "HR"]))):
    answers = await db["answers"].find({"application_id": application_id}).to_list(100)
    return answers
