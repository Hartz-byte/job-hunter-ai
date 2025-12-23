from jinja2 import Template
from typing import Dict, List
from app.resume.models import ResumeData
import os
from datetime import datetime

class ResumeTailor:
    """Generate tailored resumes without API (using templates + local processing)"""
    
    ATS_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; line-height: 1.4; color: #333; margin: 0.5in; font-size: 11pt; }
            h1 { font-size: 14pt; font-weight: bold; margin-bottom: 2pt; }
            h2 { font-size: 11pt; font-weight: bold; margin-top: 8pt; margin-bottom: 4pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; }
            p { margin: 2pt 0; }
            ul { margin: 4pt 0 4pt 20pt; }
            li { margin: 2pt 0; }
            .header { margin-bottom: 8pt; }
            .contact { font-size: 10pt; margin-top: 2pt; }
            .section { margin-top: 8pt; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ full_name }}</h1>
            <div class="contact">
                {% if email %}{{ email }}{% endif %}
                {% if phone %} | {{ phone }}{% endif %}
                {% if location %} | {{ location }}{% endif %}
            </div>
        </div>
        
        {% if summary %}
        <div class="section">
            <h2>Professional Summary</h2>
            <p>{{ summary }}</p>
        </div>
        {% endif %}
        
        {% if technical_skills %}
        <div class="section">
            <h2>Technical Skills</h2>
            <p>{{ technical_skills_text }}</p>
        </div>
        {% endif %}
        
        {% if soft_skills %}
        <div class="section">
            <h2>Core Competencies</h2>
            <p>{{ soft_skills_text }}</p>
        </div>
        {% endif %}
        
        {% if work_experience %}
        <div class="section">
            <h2>Professional Experience</h2>
            {% for exp in work_experience %}
            <p><strong>{{ exp.job_title }}</strong> | {{ exp.company }} | {{ exp.duration }}</p>
            <ul>
            {% for bullet in exp.bullets %}
                <li>{{ bullet }}</li>
            {% endfor %}
            </ul>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if education %}
        <div class="section">
            <h2>Education</h2>
            {% for edu in education %}
            <p><strong>{{ edu.degree }}</strong> in {{ edu.field }} | {{ edu.school }} | {{ edu.year }}
            {% if edu.gpa %} (GPA: {{ edu.gpa }}){% endif %}
            </p>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if certifications %}
        <div class="section">
            <h2>Certifications & Achievements</h2>
            <ul>
            {% for cert in certifications %}
                <li>{{ cert }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
    </body>
    </html>
    """
    
    def generate_resume_html(self, resume_data: ResumeData, job_title: str = None) -> str:
        """Generate ATS-friendly resume HTML"""
        
        # Tailor summary if job title provided
        summary = resume_data.summary
        if job_title:
            # Simple keyword injection - no API needed
            summary = f"Results-driven professional skilled in {', '.join(resume_data.technical_skills[:3])}. Proven expertise in {job_title}."
        
        template = Template(self.ATS_TEMPLATE)
        
        context = {
            'full_name': resume_data.full_name,
            'email': resume_data.email,
            'phone': resume_data.phone,
            'location': resume_data.location,
            'summary': summary,
            'technical_skills_text': ', '.join(resume_data.technical_skills[:15]),
            'soft_skills_text': ', '.join(resume_data.soft_skills[:10]),
            'work_experience': [
                {
                    'job_title': exp.job_title,
                    'company': exp.company,
                    'duration': exp.duration,
                    'bullets': exp.description.split('\n')[:5]
                } for exp in resume_data.work_experience
            ],
            'education': resume_data.education,
            'certifications': resume_data.certifications
        }
        
        return template.render(context)
    
    def html_to_pdf(self, html_content: str, output_path: str):
        """Convert HTML to PDF using WeasyPrint"""
        from weasyprint import HTML
        try:
            HTML(string=html_content).write_pdf(output_path)
            return output_path
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise
    
    def html_to_docx(self, html_content: str, output_path: str):
        """Convert HTML to DOCX"""
        from docx import Document
        from docx.shared import Pt, Inches
        
        doc = Document()
        
        # Very basic conversion - just adds text
        # In production, use a proper HTML-to-DOCX converter
        soup_text = html_content.replace('<br/>', '\n').replace('<br>', '\n')
        doc.add_paragraph(soup_text)
        
        doc.save(output_path)
        return output_path
