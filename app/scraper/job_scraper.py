from app.scraper.sources.indeed import IndeedScraper
from app.scraper.sources.linkedin import LinkedInJobsScraper
from app.scraper.sources.remoteok import RemoteOKScraper
from app.database.database import get_db_session
from app.database.models import Job
from typing import List, Optional
from datetime import datetime
import json

class JobScraper:
    """Unified job scraper"""
    
    def __init__(self):
        self.sources = [
            LinkedInJobsScraper(),
            RemoteOKScraper(),
            IndeedScraper(),
        ]
    
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
        
        import uuid

        for source in self.sources:
            try:
                source_name = source.__class__.__name__
                print(f"Scraping {source_name}...")
                
                # Dynamic dispatch based on signature would be better, but simpler here:
                if isinstance(source, RemoteOKScraper):
                     # RemoteOK is global/remote, location might filter it
                     jobs = source.search_jobs(query, location, limit=limit)
                else:
                    jobs = source.search_jobs(query, location, limit=limit)
                
                # Assign unique IDs to transient jobs
                for job in jobs:
                    if 'id' not in job:
                        job['id'] = str(uuid.uuid4())

                print(f"Found {len(jobs)} jobs on {source_name}")
                all_jobs.extend(jobs)
                
            except Exception as e:
                print(f"Error scraping {source.__class__.__name__}: {e}")
        
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
