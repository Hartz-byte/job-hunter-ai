from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
import json

class JobMatcher:
    """Match jobs with resume using free embeddings (NO API CALLS)"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with sentence transformer model
        all-MiniLM-L6-v2: Fast, lightweight, good for your specs
        """
        print("Loading embedding model (one-time download: 90MB)...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")
    
    def calculate_match_score(
        self,
        resume_text: str,
        job_description: str,
        resume_skills: List[str],
        job_title: str
    ) -> Dict:
        """
        Calculate match score between resume and job
        Using semantic similarity (NO LLM API CALLS)
        """
        
        # Combine texts for embedding
        resume_embedding = self.model.encode(resume_text)
        job_embedding = self.model.encode(job_description)
        
        # Calculate cosine similarity (0-1 score)
        semantic_score = cosine_similarity([resume_embedding], [job_embedding])
        semantic_score = float(semantic_score) * 100  # Convert to 0-100
        
        # Skill matching
        job_desc_lower = job_description.lower()
        matched_skills = []
        for skill in resume_skills:
            if skill.lower() in job_desc_lower:
                matched_skills.append(skill)
        
        # Extract job requirements (simple heuristic)
        missing_skills = []
        if "required" in job_desc_lower:
            # Very basic parsing - in production use better NLP
            pass
        
        # Calculate final score
        skill_bonus = (len(matched_skills) / max(len(resume_skills), 1)) * 30
        final_score = min(100, semantic_score * 0.7 + skill_bonus)
        
        return {
            'match_score': round(final_score, 2),
            'semantic_score': round(semantic_score, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'recommendation': self._get_recommendation(final_score)
        }
    
    @staticmethod
    def _get_recommendation(score: float) -> str:
        """Get recommendation based on score"""
        if score >= 80:
            return "strong_match"
        elif score >= 60:
            return "good_match"
        elif score >= 40:
            return "moderate_match"
        else:
            return "poor_match"
    
    def rank_jobs(
        self,
        resume_text: str,
        resume_skills: List[str],
        jobs: List[Dict]
    ) -> List[Dict]:
        """Rank multiple jobs"""
        ranked = []
        
        for job in jobs:
            match = self.calculate_match_score(
                resume_text,
                job['description'],
                resume_skills,
                job['title']
            )
            
            ranked.append({
                'job': job,
                'match': match
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x['match']['match_score'], reverse=True)
        return ranked
