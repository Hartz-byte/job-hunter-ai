from pydantic import BaseModel, Field
from typing import List, Optional

class WorkExperience(BaseModel):
    company: str
    job_title: str
    duration: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str
    key_skills: List[str] = []

class Education(BaseModel):
    school: str
    degree: str
    field: str
    year: str
    gpa: Optional[str] = None

class ResumeData(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    certifications: List[str] = []
    projects: List[dict] = []
    years_of_experience: int = 0

class JobPreferences(BaseModel):
    job_title: Optional[str] = None
    experience_level: Optional[str] = None  # entry, mid, senior
    job_type: List[str] = ["remote", "hybrid", "on-site"]
    locations: List[str] = []
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    industries: List[str] = []
    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []
