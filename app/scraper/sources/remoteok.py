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
                
                # Smart query matching
                q_lower = query.lower()
                
                # 1. Expand common acronyms
                if "ml " in q_lower or q_lower == "ml":
                    q_lower = q_lower.replace("ml", "machine learning")
                if "ai " in q_lower or q_lower == "ai":
                    q_lower = q_lower.replace("ai", "artificial intelligence")
                
                # 2. Check for match
                # Convert query to set of terms for flexible matching
                query_terms = set(q_lower.split())
                
                # Check if all terms exist in the search text
                # We use >= to allow partial matches if the query is long, but for short queries we want all
                match_count = sum(1 for term in query_terms if term in search_text)
                match_ratio = match_count / len(query_terms) if query_terms else 0
                
                # Strict match for short queries, looser for long ones
                if len(query_terms) <= 2:
                    if match_count != len(query_terms):
                         # Fallback: check if the FULL query string appears as a substring
                         if q_lower not in search_text:
                             continue
                else:
                    if match_ratio < 0.33: # Allow missing 2 words out of 3 - VERY loose
                        continue

                # Check location if specified
                # Allow "Remote" or "Worldwide" or missing location (often implies remote)
                job_loc = item.get('location', 'remote').lower() 
                if not job_loc: job_loc = "remote"
                
                if location:
                    loc_query = location.lower()
                    
                    # If user SPECIFICALLY searches for "Remote", we include all remote jobs
                    if loc_query == 'remote':
                        pass # Do not filter, as most jobs here are remote
                    
                    # If user searches for a specific place (e.g. Bangalore), we check for it
                    # But we ALSO include jobs marked as "Worldwide" or "Anywhere" or "Remote" if the user didn't explicitly forbid it
                    else:
                        if (loc_query not in job_loc and 
                            'worldwide' not in job_loc and
                            'anywhere' not in job_loc and
                            'remote' not in job_loc): # Keep remote jobs visibly unless excluded
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
            
        # Fallback: If no jobs found with specific location key, try relaxing location filter
        if not jobs and location:
             print(f"[RemoteOK] No jobs found for '{location}'. Retrying without location filter...")
             # Recursive call but without location
             # Prevent infinite recursion by checking if location is already empty
             return self.search_jobs(query, location="", limit=limit)
        
        return jobs
