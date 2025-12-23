import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
import time

class IndeedScraper:
    """Scrape Indeed jobs (without Selenium for speed)"""
    
    BASE_URL = "https://indeed.com/jobs"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        job_type: str = None,
        experience_level: str = None,
        limit: int = 50
    ) -> List[dict]:
        """Search jobs on Indeed"""
        jobs = []
        pages = (limit // 10) + 1
        
        for page in range(pages):
            try:
                params = {
                    'q': query,
                    'l': location,
                    'start': page * 10,
                    'limit': 10
                }
                
                if job_type:
                    params['jt'] = job_type
                
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName')
                        location_elem = card.find('div', class_='companyLocation')
                        snippet = card.find('div', class_='job-snippet')
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else location,
                                'description': snippet.get_text(strip=True) if snippet else '',
                                'url': title_elem.find('a')['href'] if title_elem.find('a') else '',
                                'source': 'indeed',
                                'posted_date': datetime.now(),
                                'job_type': job_type or 'not specified',
                                'experience_level': experience_level or 'not specified'
                            }
                            jobs.append(job)
                    except:
                        continue
                
                time.sleep(2)  # Be respectful to servers
                
            except Exception as e:
                print(f"Error scraping Indeed page {page}: {e}")
                continue
        
        return jobs[:limit]
