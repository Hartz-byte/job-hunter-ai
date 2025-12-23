import PyPDF2
from typing import Optional
from app.resume.models import ResumeData, WorkExperience, Education
import re

class ResumeParser:
    """Parse resume PDF without using any API"""
    
    @staticmethod
    def extract_pdf_text(pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            raise ValueError(f"Could not extract text from PDF: {e}")
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email from text"""
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number"""
        # Support Indian format: +91-XXXXX-XXXXX or 10 digit
        patterns = [
            r'\+91[\s\-]?\d{5}[\s\-]?\d{5}',
            r'\+91[\s\-]?\d{10}',
            r'[\d\s\-\+]{10,}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    @staticmethod
    def extract_name(text: str) -> Optional[str]:
        """Extract name from first lines"""
        lines = text.split('\n')[:5]
        # Usually name is in first few lines and is likely capitalized
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line) < 50:
                # Check if it looks like a name (mostly capitals)
                words = line.split()
                if len(words) <= 3 and all(w.isupper() for w in words if w):
                    return line
        return "Name Not Found"
    
    @staticmethod
    def extract_section(text: str, section_name: str, end_marker: Optional[str] = None) -> str:
        """Extract section between headers"""
        # Common section headers
        headers = [
            f"{section_name.upper()}",
            f"{section_name.upper()}S",
            f"## {section_name}",
            f"• {section_name}",
        ]
        
        text_upper = text.upper()
        start_idx = -1
        
        for header in headers:
            idx = text_upper.find(header)
            if idx != -1:
                start_idx = idx
                break
        
        if start_idx == -1:
            return ""
        
        # Find end of section
        end_idx = len(text)
        if end_marker:
            end_idx = text_upper.find(end_marker.upper(), start_idx)
            if end_idx == -1:
                end_idx = len(text)
        
        section_text = text[start_idx:end_idx]
        return section_text
    
    @staticmethod
    def parse_skills(text: str) -> tuple:
        """Extract technical and soft skills"""
        # Common technical skills
        tech_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Django', 'FastAPI', 'Flask', 'Spring', 'Node',
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Keras',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure', 'CI/CD', 'Git', 'Jenkins',
            'Linux', 'REST API', 'GraphQL', 'Microservices', 'Machine Learning',
            'Deep Learning', 'NLP', 'Computer Vision', 'Data Science'
        ]
        
        # Common soft skills
        soft_keywords = [
            'Communication', 'Leadership', 'Problem Solving', 'Teamwork',
            'Project Management', 'Critical Thinking', 'Adaptability', 'Creativity',
            'Time Management', 'Collaboration'
        ]
        
        technical_skills = []
        soft_skills = []
        
        for skill in tech_keywords:
            if skill.lower() in text.lower():
                technical_skills.append(skill)
        
        for skill in soft_keywords:
            if skill.lower() in text.lower():
                soft_skills.append(skill)
        
        return list(set(technical_skills)), list(set(soft_skills))
    
    @staticmethod
    def calculate_experience_years(text: str) -> int:
        """Estimate years of experience from dates"""
        from datetime import datetime
        import re
        
        # Find all year patterns
        years = re.findall(r'\b(20\d{2})\b', text)
        if not years:
            return 0
        
        years = [int(y) for y in years]
        if len(years) >= 2:
            return min(years[-1] - years, 20)  # Cap at 20 years
        return 0
    
    def parse_resume(self, pdf_path: str) -> ResumeData:
        """Parse entire resume and return structured data"""
        # Extract text
        text = self.extract_pdf_text(pdf_path)
        
        # Extract basic info
        name = self.extract_name(text)
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        
        # Extract sections
        summary_section = self.extract_section(text, "SUMMARY")
        skills_section = self.extract_section(text, "SKILLS")
        
        # Parse skills
        technical_skills, soft_skills = self.parse_skills(text)
        
        # Calculate experience
        years_exp = self.calculate_experience_years(text)
        
        # Simple heuristic for location (often near phone number)
        location = "Bangalore"  # Default
        
        return ResumeData(
            full_name=name or "Unknown",
            email=email or "not@found.com",
            phone=phone or "+91-0000000000",
            location=location,
            summary=summary_section[:200] if summary_section else "ML/Software Engineer",
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            years_of_experience=years_exp,
            work_experience=[],  # Would require more sophisticated parsing
            education=[],
            certifications=[]
        )
