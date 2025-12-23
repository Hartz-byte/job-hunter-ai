from app.scraper.sources.indeed import IndeedScraper
from app.scraper.sources.github import GitHubJobsScraper
from app.scraper.sources.stackoverflow import StackOverflowScraper
from app.database.database import get_db_session
from app.database.models import Job
from typing import List, Optional
from datetime import datetime
import json

class JobScraper:
    """Unified job scraper"""
    
    def __init__(self):
        self.indeed = IndeedScraper()
        self.github = GitHubJobsScraper()
        self.stackoverflow = StackOverflowScraper()
    
    def search_all_sources(
        self,
        query: str,
        location: str = "India",
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        limit: int = 50
    ) -> List[dict]:
        """Search all job sources"""
        all_jobs = []
        
        print(f"Scraping jobs for: {query} in {location}")
        
        # GitHub Jobs (easiest, API-based)
        try:
            print("Scraping GitHub Jobs...")
            github_jobs = self.github.search_jobs(query, location, limit=limit//3)
            all_jobs.extend(github_jobs)
            print(f"Found {len(github_jobs)} jobs on GitHub")
        except Exception as e:
            print(f"GitHub scraping error: {e}")
        
        # Stack Overflow
        try:
            print("Scraping Stack Overflow...")
            so_jobs = self.stackoverflow.search_jobs(
                query,
                location=location,
                experience_level=experience_level,
                limit=limit//3
            )
            all_jobs.extend(so_jobs)
            print(f"Found {len(so_jobs)} jobs on Stack Overflow")
        except Exception as e:
            print(f"Stack Overflow scraping error: {e}")
        
        # Indeed (if you want, comment out if too slow)
        try:
            print("Scraping Indeed...")
            indeed_jobs = self.indeed.search_jobs(
                query,
                location=location,
                job_type=job_type,
                experience_level=experience_level,
                limit=limit//3
            )
            all_jobs.extend(indeed_jobs)
            print(f"Found {len(indeed_jobs)} jobs on Indeed")
        except Exception as e:
            print(f"Indeed scraping error: {e}")
        
        return all_jobs[:limit]
    
    def save_jobs_to_db(self, jobs: List[dict]):
        """Save jobs to database"""
        db = get_db_session()
        try:
            for job_data in jobs:
                # Check if job already exists
                existing = db.query(Job).filter(Job.url == job_data['url']).first()
                if existing:
                    continue
                
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    description=job_data['description'],
                    location=job_data['location'],
                    job_type=job_data.get('job_type', 'not specified'),
                    url=job_data['url'],
                    source=job_data['source'],
                    posted_date=job_data.get('posted_date', datetime.now()),
                    experience_level=job_data.get('experience_level', 'not specified'),
                    parsed_data=json.dumps(job_data)
                )
                db.add(job)
            
            db.commit()
            print(f"Saved {len(jobs)} jobs to database")
        except Exception as e:
            print(f"Error saving jobs: {e}")
            db.rollback()
        finally:
            db.close()
