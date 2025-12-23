import requests
from datetime import datetime
from typing import List

class RemoteOKScraper:
    """Scrape RemoteOK jobs (Public API)"""
    
    BASE_URL = "https://remoteok.com/api"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_jobs(
        self,
        query: str,
        location: str = "",
        limit: int = 50
    ) -> List[dict]:
        """Search jobs on RemoteOK"""
        jobs = []
        
        try:
            # RemoteOK uses tags for filtering
            # We'll map the query to a tag if possible, or just search filtered result
            
            # The API returns all jobs, we need to filter client-side for query
            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                timeout=20
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Filter and map jobs
            # Index 0 is legal disclaimer, skip it
            for item in data[1:]:
                if len(jobs) >= limit:
                    break
                    
                # Basic fuzzy search for query in title/description/tags
                search_text = (
                    f"{item.get('position', '')} "
                    f"{item.get('company', '')} "
                    f"{' '.join(item.get('tags', []))}"
                ).lower()
                
                if query.lower() in search_text:
                    # Check location if specified
                    job_loc = item.get('location', '').lower()
                    if location and location.lower() not in job_loc and 'remote' not in job_loc:
                        continue

                    job = {
                        'title': item.get('position', ''),
                        'company': item.get('company', ''),
                        'location': item.get('location', 'Remote'),
                        'description': item.get('description', ''),
                        'url': item.get('url', ''),
                        'source': 'remoteok',
                        'posted_date': datetime.fromisoformat(
                            item.get('date', '').replace('Z', '+00:00')
                        ) if item.get('date') else datetime.now(),
                        'job_type': 'remote',
                        'experience_level': 'not specified'
                    }
                    jobs.append(job)
        
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")
        
        return jobs
