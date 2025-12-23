import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
import time

class StackOverflowScraper:
    """Scrape Stack Overflow Jobs"""
    
    BASE_URL = "https://stackoverflow.com/jobs"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_jobs(
        self,
        query: str,
        location: str = "",
        experience_level: str = None,
        limit: int = 50
    ) -> List[dict]:
        """Search jobs on Stack Overflow"""
        jobs = []
        pages = (limit // 15) + 1
        
        try:
            for page in range(pages):
                params = {
                    'q': query,
                    'pg': page + 1
                }
                
                if location:
                    params['l'] = location
                
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings
                job_cards = soup.find_all('div', class_='s-post-summary')
                
                for card in job_cards[:15]:
                    try:
                        title_elem = card.find('h2')
                        company_elem = card.find('h3')
                        location_elem = card.find('span', class_='fc-black-400')
                        
                        if title_elem:
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                                'location': location_elem.get_text(strip=True) if location_elem else location,
                                'description': card.get_text(strip=True)[:500],
                                'url': title_elem.find('a')['href'] if title_elem.find('a') else '',
                                'source': 'stackoverflow',
                                'posted_date': datetime.now(),
                                'job_type': 'remote' if 'remote' in card.get_text().lower() else 'on-site',
                                'experience_level': experience_level or 'not specified'
                            }
                            jobs.append(job)
                    except:
                        continue
                
                time.sleep(2)
                
        except Exception as e:
            print(f"Error scraping Stack Overflow: {e}")
        
        return jobs[:limit]
