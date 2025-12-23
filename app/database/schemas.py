# Database Schemas - Pydantic Models for API Requests/Responses

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ============ Resume Schemas ============

class WorkExperienceSchema(BaseModel):
    company: str
    job_title: str
    duration: str
    description: str
    key_skills: List[str] = []

class EducationSchema(BaseModel):
    school: str
    degree: str
    field: str
    year: str
    gpa: Optional[str] = None

class ResumeUploadResponse(BaseModel):
    status: str
    message: str
    user_id: str
    resume: dict

class ResumeDataSchema(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    summary: Optional[str] = None
    work_experience: List[WorkExperienceSchema] = []
    education: List[EducationSchema] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    certifications: List[str] = []
    projects: List[dict] = []
    years_of_experience: int = 0

# ============ Job Search Schemas ============

class JobPreferencesSchema(BaseModel):
    job_title: Optional[str] = None
    experience_level: Optional[str] = None  # entry, mid, senior
    job_type: List[str] = ["remote", "hybrid", "on-site"]
    locations: List[str] = []
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    industries: List[str] = []
    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []

class JobSchema(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    description: str
    location: str
    job_type: Optional[str] = None
    url: str
    source: str
    salary: Optional[str] = None
    posted_date: Optional[datetime] = None
    experience_level: Optional[str] = None

class JobSearchResponse(BaseModel):
    status: str
    total: int
    jobs: List[JobSchema]

# ============ Job Matching Schemas ============

class JobMatchSchema(BaseModel):
    match_score: float
    semantic_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendation: str  # strong_match, good_match, moderate_match, poor_match

class JobMatchDetailSchema(BaseModel):
    job: JobSchema
    match: JobMatchSchema

class JobMatchResponse(BaseModel):
    status: str
    total: int
    jobs: List[JobMatchDetailSchema]

# ============ Document Generation Schemas ============

class ResumeTailorRequest(BaseModel):
    job_title: str
    output_format: str = "pdf"  # pdf or docx

class ResumeTailorResponse(BaseModel):
    status: str
    download_url: str
    file_path: str

class CoverLetterRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: Optional[str] = None

class CoverLetterResponse(BaseModel):
    status: str
    content: str
    download_url: str

# ============ Application Status Schemas ============

class SavedJobSchema(BaseModel):
    id: str
    user_id: str
    job_id: str
    status: str  # shortlisted, applied, rejected
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    created_at: datetime

class ApplicationHistoryResponse(BaseModel):
    total: int
    saved_jobs: List[SavedJobSchema]

# ============ API Error Schemas ============

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[dict] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str = "1.0.0"

# ============ Bulk Operations Schemas ============

class BulkGenerateRequest(BaseModel):
    job_ids: List[str]
    output_format: str = "pdf"

class BulkGenerateResponse(BaseModel):
    status: str
    total: int
    generated: int
    failed: int
    files: List[dict]  # List of {job_id, file_path, download_url}

class BatchJobSearchRequest(BaseModel):
    queries: List[str]
    location: str = "India"
    limit: int = 20

class BatchJobSearchResponse(BaseModel):
    status: str
    total: int
    results: List[JobSearchResponse]
