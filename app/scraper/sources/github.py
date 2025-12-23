import requests
import json
from datetime import datetime
from typing import List

class GitHubJobsScraper:
    """Scrape GitHub Jobs (public API, no auth needed)"""
    
    # GitHub Jobs API is deprecated, using alternative
    BASE_URL = "https://jobs.github.com/positions.json"
    
    def search_jobs(
        self,
        query: str,
        location: str = "",
        full_time: bool = True,
        limit: int = 50
    ) -> List[dict]:
        """Search jobs on GitHub Jobs"""
        jobs = []
        
        try:
            params = {
                'description': query,
                'full_time': str(full_time).lower(),
            }
            
            if location:
                params['location'] = location
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            for item in data[:limit]:
                job = {
                    'title': item.get('title', ''),
                    'company': item.get('company', ''),
                    'location': item.get('location', location),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'source': 'github',
                    'posted_date': datetime.fromisoformat(
                        item.get('created_at', '').replace('Z', '+00:00')
                    ) if item.get('created_at') else datetime.now(),
                    'job_type': 'remote' if 'remote' in item.get('description', '').lower() else 'on-site',
                    'experience_level': 'not specified'
                }
                jobs.append(job)
        
        except Exception as e:
            print(f"Error scraping GitHub Jobs: {e}")
        
        return jobs
