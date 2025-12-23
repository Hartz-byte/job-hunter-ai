import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ollama
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./job_hunter.db")
    
    # Job Scraping
    JOB_SCRAPE_LIMIT = int(os.getenv("JOB_SCRAPE_LIMIT", "50"))
    SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Job Preferences
    DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "Bangalore")
    DEFAULT_JOB_TYPE = os.getenv("DEFAULT_JOB_TYPE", "remote,hybrid,on-site")

config = Config()
