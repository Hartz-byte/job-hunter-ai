# LinkedIn Jobs Scraper
# Note: LinkedIn heavily restricts scraping. This uses RSS feeds and public job listings.
# For production use, consider using official LinkedIn API (requires approval)

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
import time
import json

class LinkedInJobsScraper:
    """
    Scrape LinkedIn Jobs using public RSS feeds and alternative methods.
    Note: LinkedIn's Terms of Service restrict automated scraping.
    This implementation uses public RSS feeds where available.
    """
    
    BASE_URL = "https://www.linkedin.com/jobs/api/jobPosting"
    RSS_BASE = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
    
    def search_jobs_rss(
        self,
        query: str,
        location: str = "India",
        limit: int = 20
    ) -> List[dict]:
        """
        Search LinkedIn jobs using public job search endpoint (RSS-style).
        This is more respectful to LinkedIn's servers.
        """
        jobs = []
        
        try:
            # LinkedIn Jobs search endpoint (unofficial but public)
            search_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
            params = {
                'keywords': query,
                'location': location,
                'geoId': '102713980',  # India geo ID
                'start': 0,
                'count': min(limit, 25),
                'position': 1,
                'pageNum': 0,
                'sortBy': 'DD'  # Most recent
            }
            
            response = self.session.get(
                search_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            # Parse response
            if response.status_code == 200:
                try:
                    # LinkedIn returns HTML, parse it
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-card')
                    
                    for card in job_cards[:limit]:
                        try:
                            # Extract job details
                            title_elem = card.find('h3', class_='base-search-card__title')
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            location_elem = card.find('span', class_='job-search-card__location')
                            link_elem = card.find('a', class_='base-card__full-link')
                            
                            if title_elem and company_elem:
                                job = {
                                    'title': title_elem.get_text(strip=True),
                                    'company': company_elem.get_text(strip=True),
                                    'location': location_elem.get_text(strip=True) if location_elem else location,
                                    'description': card.get_text(strip=True)[:500],
                                    'url': link_elem.get('href', '') if link_elem else '',
                                    'source': 'linkedin',
                                    'posted_date': datetime.now(),
                                    'job_type': 'not specified',
                                    'experience_level': 'not specified'
                                }
                                jobs.append(job)
                        except Exception as e:
                            print(f"Error parsing LinkedIn job card: {e}")
                            continue
                
                except Exception as e:
                    print(f"Error parsing LinkedIn response: {e}")
            
            time.sleep(1)  # Be respectful
            
        except Exception as e:
            print(f"Error searching LinkedIn jobs: {e}")
        
        return jobs
    
    def search_jobs_alternative(
        self,
        query: str,
        location: str = "India",
        limit: int = 20
    ) -> List[dict]:
        """
        Alternative method using LinkedIn job feed (if available).
        Falls back gracefully if LinkedIn blocks requests.
        """
        jobs = []
        
        try:
            # Use LinkedIn's public job search
            # Note: This may require occasional CAPTCHA solving
            search_url = "https://www.linkedin.com/jobs/search"
            
            params = {
                'keywords': query,
                'location': location,
                'sortBy': 'DD'
            }
            
            response = requests.get(
                search_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract job listings from the page
                job_containers = soup.find_all('div', {'data-job-id': True})
                
                for container in job_containers[:limit]:
                    try:
                        job_id = container.get('data-job-id', '')
                        job_title = container.find('h3')
                        job_company = container.find('h4')
                        
                        if job_title and job_company:
                            job = {
                                'title': job_title.get_text(strip=True),
                                'company': job_company.get_text(strip=True),
                                'location': location,
                                'description': container.get_text(strip=True)[:500],
                                'url': f'https://www.linkedin.com/jobs/view/{job_id}' if job_id else '',
                                'source': 'linkedin',
                                'posted_date': datetime.now(),
                                'job_type': 'not specified',
                                'experience_level': 'not specified'
                            }
                            jobs.append(job)
                    except:
                        continue
            
            time.sleep(1)
        
        except Exception as e:
            print(f"Error with alternative LinkedIn scraping: {e}")
        
        return jobs
    
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        limit: int = 20
    ) -> List[dict]:
        """
        Main search method - tries multiple approaches.
        Falls back gracefully if LinkedIn blocks requests.
        """
        print(f"[LinkedIn] Searching for: {query} in {location}")
        
        # Try RSS method first (more respectful)
        jobs = self.search_jobs_rss(query, location, limit)
        
        if len(jobs) < limit // 2:
            print(f"[LinkedIn] Got {len(jobs)} jobs from RSS, trying alternative method...")
            # Try alternative method as fallback
            alt_jobs = self.search_jobs_alternative(query, location, limit - len(jobs))
            jobs.extend(alt_jobs)
        
        print(f"[LinkedIn] Found {len(jobs)} jobs total")
        return jobs[:limit]
    
    def get_job_details(self, job_url: str) -> dict:
        """
        Get detailed job information from LinkedIn job posting URL.
        May require additional authentication.
        """
        try:
            response = requests.get(
                job_url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract job details
                description = soup.find('div', class_='show-more-less-html__markup')
                
                return {
                    'full_description': description.get_text() if description else '',
                    'url': job_url,
                    'scraped_at': datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Error getting job details: {e}")
        
        return {}


# Alternative: Using LinkedIn RSS Job Feed (if available)
class LinkedInRSSFeed:
    """
    LinkedIn RSS feed parser (if you have specific RSS feeds)
    Some companies publish their LinkedIn jobs via RSS
    """
    
    def parse_rss_feed(self, rss_url: str) -> List[dict]:
        """Parse LinkedIn RSS job feed"""
        jobs = []
        
        try:
            import xml.etree.ElementTree as ET
            
            response = requests.get(rss_url, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item'):
                    try:
                        title = item.find('title')
                        description = item.find('description')
                        link = item.find('link')
                        pub_date = item.find('pubDate')
                        
                        job = {
                            'title': title.text if title is not None else '',
                            'description': description.text if description is not None else '',
                            'url': link.text if link is not None else '',
                            'posted_date': pub_date.text if pub_date is not None else '',
                            'source': 'linkedin_rss',
                            'company': 'LinkedIn',
                            'location': 'Various',
                            'job_type': 'not specified',
                            'experience_level': 'not specified'
                        }
                        jobs.append(job)
                    except:
                        continue
        
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
        
        return jobs


# ============ IMPORTANT NOTE ============
"""
LinkedIn's Terms of Service restrict automated scraping.

Alternatives and Recommendations:
1. Use LinkedIn's Official API (requires company verification)
   - LinkedIn Talent Solutions API
   - LinkedIn Recruiter API (premium)

2. Use Job Aggregator APIs that legally gather LinkedIn jobs:
   - JSearch API (on RapidAPI)
   - Adzuna API
   - Jobs API on Rapid API
   - RemoteOK API (includes LinkedIn jobs)

3. Use web scraping libraries responsibly:
   - Respect rate limits (delays between requests)
   - Check robots.txt
   - Use residential proxies if needed
   - Implement caching to avoid repeated requests

4. Direct Company Websites:
   - Many companies post jobs directly on their career pages
   - Usually more up-to-date than LinkedIn
   - Easier to scrape (fewer restrictions)

For production use, consider using a job scraping service like:
- Apify (has pre-built LinkedIn scrapers)
- Bright Data (residential proxies + scraping)
- Serpstack (job search API)

This implementation prioritizes ethical scraping and respects LinkedIn's servers.
If LinkedIn blocks your requests, switch to free job APIs instead.
"""
