from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.database.database import get_db, init_db, get_db_session
from app.database.models import User, Job, SavedJob, GeneratedDocument
from app.resume.parser import ResumeParser
from app.resume.models import ResumeData, JobPreferences
from app.scraper.job_scraper import JobScraper
from app.matching.job_matcher import JobMatcher
from app.generation.resume_tailor import ResumeTailor
from app.generation.cover_letter import CoverLetterGenerator
import tempfile
import os
from typing import Optional
import json

# Initialize FastAPI
app = FastAPI(
    title="AI Job Hunter (Free)",
    description="Job hunting with local LLMs",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
parser = ResumeParser()
scraper = JobScraper()
matcher = None  # Will initialize after startup
tailor = ResumeTailor()
letter_gen = CoverLetterGenerator()

# Store current user data
current_user_resume = None
current_user_id = None

def ensure_user_loaded():
    """Recover user session from DB if global state is lost"""
    global current_user_resume, current_user_id
    
    if current_user_resume and current_user_id:
        return True
        
    try:
        db = get_db_session()
        # Get latest user
        user = db.query(User).order_by(User.created_at.desc()).first()
        if user and user.resume_data:
            current_user_resume = ResumeData(**user.resume_data)
            current_user_id = user.id
            db.close()
            return True
        db.close()
    except Exception as e:
        print(f"Error restoring user session: {e}")
        
    return False

@app.on_event("startup")
async def startup_event():
    """Initialize database and AI models"""
    global matcher
    print("Initializing application...")
    init_db()
    
    # Try to restore session
    if ensure_user_loaded():
        print(f"Restored session for user: {current_user_id}")
        
    print("Loading AI models (first-time download may take a moment)...")
    matcher = JobMatcher(config.OLLAMA_EMBEDDING_MODEL)
    print("Ready to serve requests!")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "AI Job Hunter is running"}

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume"""
    global current_user_resume, current_user_id
    
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Parse resume
        current_user_resume = parser.parse_resume(tmp_path)
        
        # Save to database
        db = get_db_session()
        user = User(
            resume_data=current_user_resume.model_dump(),
            preferences={}
        )
        db.add(user)
        db.commit()
        current_user_id = user.id
        db.close()
        
        # Clean up
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "message": "Resume parsed successfully",
            "user_id": user.id,
            "resume": current_user_resume.model_dump()
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )

@app.post("/api/preferences/set")
async def set_preferences(preferences: JobPreferences):
    """Set job search preferences"""
    global current_user_id
    try:
        ensure_user_loaded()
        
        if not current_user_id:
            return JSONResponse(
                status_code=400,
                content={"error": "Please upload resume first"}
            )
        
        db = get_db_session()
        user = db.query(User).filter(User.id == current_user_id).first()
        if user:
            user.preferences = preferences.model_dump()
            db.commit()
        db.close()
        
        return {"status": "success", "message": "Preferences saved"}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/user/me")
async def get_current_user():
    """Get current user data"""
    global current_user_id, current_user_resume
    try:
        ensure_user_loaded()
        
        if not current_user_id:
            return JSONResponse(
                status_code=404,
                content={"error": "No active session"}
            )
            
        db = get_db_session()
        user = db.query(User).filter(User.id == current_user_id).first()
        
        response_data = {
            "id": user.id,
            "resume": user.resume_data,
            "preferences": user.preferences
        }
        db.close()
        
        return response_data
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/jobs/search")
async def search_jobs(
    query: str,
    location: str = "India",
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    limit: int = 50
):
    """Search for jobs"""
    try:
        print(f"Searching for: {query} in {location}")
        jobs = scraper.search_all_sources(
            query=query,
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            limit=limit
        )
        
        # Save to database
        scraper.save_jobs_to_db(jobs)
        
        return {
            "status": "success",
            "total": len(jobs),
            "jobs": jobs
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/jobs/match")
async def match_jobs(query: str, limit: int = 10):
    """Find and rank jobs matching resume"""
    global matcher, current_user_resume
    try:
        ensure_user_loaded()
        
        if not current_user_resume:
            return JSONResponse(
                status_code=400,
                content={"error": "Please upload resume first"}
            )
        
        if not matcher:
            return JSONResponse(
                status_code=500,
                content={"error": "AI model not initialized"}
            )
        
        # Search jobs
        print(f"Searching for: {query}")
        jobs = scraper.search_all_sources(query, limit=limit)
        
        if not jobs:
            return {"total": 0, "jobs": []}
        
        # Prepare resume text
        resume_text = f"{current_user_resume.summary} {' '.join(current_user_resume.technical_skills)}"
        
        # Rank jobs
        print("Ranking jobs by match (this may take a moment)...")
        ranked = matcher.rank_jobs(
            resume_text,
            current_user_resume.technical_skills,
            jobs
        )
        
        # Format response
        result_jobs = []
        for item in ranked[:limit]:
            result_jobs.append({
                'job': item['job'],
                'match_score': item['match']['match_score'],
                'recommendation': item['match']['recommendation'],
                'matched_skills': item['match']['matched_skills']
            })
        
        return {
            "status": "success",
            "total": len(result_jobs),
            "jobs": result_jobs
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/resume/generate")
async def generate_tailored_resume(
    job_title: str,
    output_format: str = "pdf"
):
    """Generate tailored resume"""
    global current_user_resume, current_user_id
    try:
        ensure_user_loaded()
        
        if not current_user_resume:
            return JSONResponse(
                status_code=400,
                content={"error": "Please upload resume first"}
            )
        
        # Generate HTML
        html = tailor.generate_resume_html(current_user_resume, job_title)
        
        # Create output directory
        os.makedirs("generated_docs", exist_ok=True)
        
        # Export
        filename = f"{current_user_id}_resume_{job_title.replace(' ', '_')}"
        if output_format == "pdf":
            try:
                output_path = f"generated_docs/{filename}.pdf"
                tailor.html_to_pdf(html, output_path)
            except Exception as e:
                print(f"PDF generation failed, falling back to HTML: {e}")
                # Fallback to HTML
                output_path = f"generated_docs/{filename}.html"
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html)
        else:
            output_path = f"generated_docs/{filename}.docx"
            tailor.html_to_docx(html, output_path)
        
        return {
            "status": "success",
            "message": "Resume generated (PDF unavailable, using HTML)" if output_path.endswith('.html') else "Resume generated",
            "download_url": f"/api/downloads/{os.path.basename(output_path)}",
            "file_path": output_path
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/cover-letter/generate")
async def generate_cover_letter(
    job_title: str,
    company_name: str,
    job_description: str = ""
):
    """Generate cover letter"""
    global current_user_resume, current_user_id
    try:
        ensure_user_loaded()
        
        if not current_user_resume:
            return JSONResponse(
                status_code=400,
                content={"error": "Please upload resume first"}
            )
        
        # Generate
        content = letter_gen.generate(
            current_user_resume,
            job_title,
            company_name,
            job_description
        )
        
        # Save
        os.makedirs("generated_docs", exist_ok=True)
        filename = f"{current_user_id}_cover_letter_{company_name.replace(' ', '_')}.txt"
        output_path = f"generated_docs/{filename}"
        letter_gen.save_to_file(content, output_path)
        
        return {
            "status": "success",
            "content": content,
            "download_url": f"/api/downloads/{filename}"
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/downloads/{filename}")
async def download_file(filename: str):
    """Download generated document"""
    try:
        file_path = f"generated_docs/{filename}"
        if os.path.exists(file_path):
            return FileResponse(file_path)
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
