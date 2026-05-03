from pydantic import BaseModel, Field, EmailStr
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Optional, List, Any
from datetime import datetime

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        json_schema = handler(core_schema.str_schema())
        return json_schema

    @classmethod
    def validate(cls, v):
        return str(v)

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: EmailStr
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    mobile_number: Optional[str] = None
    role: str # "HR", "Candidate", "Technical Panel"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class JobModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    description: str
    required_skills: List[str]
    last_date: datetime
    vacancies: int
    created_by: Optional[str] = None # HR email
    status: str = "Active" # "Active", "Deadline Passed", "Closed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class ApplicationModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    job_id: str
    candidate_name: Optional[str] = "N/A"
    candidate_email: str
    candidate_mobile: Optional[str] = "N/A"
    resume_file_id: str # GridFS file id
    status: str = "Applied" # "Applied", "Shortlisted", "Rejected", "Technical Assigned", "Final Selected"
    ai_score: Optional[float] = None
    ai_feedback: Optional[str] = None
    applied_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class QuestionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    job_id: str
    question_text: str
    options: List[str] = Field(default_factory=list) # For MCQ
    correct_answer: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AnswerModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    application_id: str
    question_id: str
    answer_text: str
    score: Optional[int] = None # Evaluated by technical panel
    feedback: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    application_id: str
    document_type: str # "Aadhar", "Degree", etc.
    file_id: str # GridFS
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
