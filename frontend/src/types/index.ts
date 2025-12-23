export interface ResumeData {
    full_name: string;
    email: string;
    phone: string;
    location: string;
    summary: string;
    technical_skills: string[];
    soft_skills: string[];
    years_of_experience: number;
}

export interface JobPreferences {
    job_title: string;
    experience_level: string;
    job_type: string[];
    locations: string[];
    min_salary: number;
    max_salary: number;
    industries: string[];
    required_skills: string[];
    nice_to_have_skills: string[];
}

export interface Job {
    id: string;
    title: string;
    company: string;
    location: string;
    description: string;
    url: string;
    source: string;
    job_type: string;
    posted_date: string;
    salary: string;
    match_score?: number;
    recommendation?: string;
    matched_skills?: string[];
}

export interface MatchResult {
    job: Job;
    match_score: number;
    recommendation: string;
    matched_skills: string[];
}
