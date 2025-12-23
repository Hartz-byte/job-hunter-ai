from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    resume_data = Column(JSON)  # Parsed resume as JSON
    preferences = Column(JSON)  # Job search preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    company = Column(String, index=True)
    description = Column(Text)
    location = Column(String, index=True)
    job_type = Column(String)  # remote, hybrid, on-site
    url = Column(String, unique=True)
    source = Column(String)  # indeed, github, stackoverflow, linkedin
    salary = Column(String, nullable=True)
    posted_date = Column(DateTime, nullable=True)
    experience_level = Column(String)  # entry, mid, senior
    parsed_data = Column(JSON)  # Structured job data
    created_at = Column(DateTime, default=datetime.utcnow)

class SavedJob(Base):
    __tablename__ = "saved_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    job_id = Column(String, index=True)
    status = Column(String)  # shortlisted, applied, rejected
    match_score = Column(Float)
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedDocument(Base):
    __tablename__ = "generated_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    job_id = Column(String, index=True)
    doc_type = Column(String)  # resume, cover_letter
    file_path = Column(String)
    file_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
