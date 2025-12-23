from typing import Dict
from datetime import datetime
from app.resume.models import ResumeData

class CoverLetterGenerator:
    """Generate cover letters using templates (NO API CALLS)"""
    
    TEMPLATE = """
    {contact_info}
    
    {date}
    
    Dear Hiring Manager,
    
    I am writing to express my strong interest in the {job_title} position at {company_name}. 
    With {years_exp} years of experience in {primary_skills}, I am confident in my ability to 
    contribute effectively to your team and help achieve your organization's goals.
    
    In my current role at {current_company}, I have successfully {achievement1}. 
    Additionally, I {achievement2}. These experiences have equipped me with strong 
    problem-solving skills, attention to detail, and the ability to work effectively in 
    collaborative environments.
    
    I am particularly interested in {company_name} because {company_interest}. 
    I believe my technical skills in {relevant_skills} and my passion for {role_interest} 
    make me an excellent fit for this role. I am excited about the opportunity to bring 
    my expertise and enthusiasm to your organization.
    
    I would welcome the opportunity to discuss how my background, skills, and abilities 
    align with your team's needs. Thank you for considering my application. I look forward 
    to speaking with you soon.
    
    Sincerely,
    {full_name}
    {email}
    {phone}
    """
    
    def __init__(self):
        pass
    
    def generate(
        self,
        resume: ResumeData,
        job_title: str,
        company_name: str,
        job_description: str = ""
    ) -> str:
        """Generate customized cover letter"""
        
        # Extract some achievements from resume
        achievement1 = "driven key projects"
        achievement2 = "demonstrated leadership and technical proficiency"
        
        if resume.work_experience:
            exp = resume.work_experience
            achievement1 = exp.description.split('\n')[:100] if exp.description else achievement1
        
        # Build context
        context = {
            'contact_info': f"{resume.full_name}\n{resume.email}\n{resume.phone}\n{resume.location}",
            'date': datetime.now().strftime("%B %d, %Y"),
            'job_title': job_title,
            'company_name': company_name,
            'years_exp': resume.years_of_experience,
            'primary_skills': ', '.join(resume.technical_skills[:2]) if resume.technical_skills else 'software development',
            'current_company': resume.work_experience.company if resume.work_experience else 'my current position',
            'achievement1': achievement1,
            'achievement2': achievement2,
            'company_interest': f"of its reputation and involvement in {job_title}",
            'relevant_skills': ', '.join(resume.technical_skills[:3]) if resume.technical_skills else 'technology',
            'role_interest': job_description[:50] if job_description else 'software engineering',
            'full_name': resume.full_name,
            'email': resume.email,
            'phone': resume.phone
        }
        
        # Format template
        letter = self.TEMPLATE.format(**context)
        return letter
    
    def save_to_file(self, content: str, output_path: str):
        """Save cover letter to file"""
        with open(output_path, 'w') as f:
            f.write(content)
        return output_path
