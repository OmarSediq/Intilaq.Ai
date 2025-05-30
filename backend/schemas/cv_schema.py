from pydantic import BaseModel, EmailStr,HttpUrl
from typing import Optional
from datetime import date

class HeaderRequest(BaseModel):
    full_name: str
    job_title: Optional[str]=None #  input for objective  
    email: EmailStr
    phone_number: Optional[str]=None
    address: Optional[str]=None
    linkedin_profile: Optional[str]=None
    github_profile: Optional[str]=None
    years_of_experience: Optional[int]=None #  input for objective 

class ExperienceRequest(BaseModel):
   
    role: str
    start_date: date
    end_date: Optional[date]
    company_name: Optional[str] = None

    @staticmethod
    def validate_dates(start_date: date, end_date: Optional[date]):
        if end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date")

class ExperienceSaveRequest(BaseModel):
    
    role: str
    selected_description: str


# Education
class EducationRequest(BaseModel):
    
    degree_and_major: str
    school: str
    city: Optional[str]
    country: Optional[str]
    start_date: date
    end_date: Optional[date]
    description: Optional[str]

class SkillsLanguagesRequest(BaseModel):
    languages: str  
    skills: Optional[str] = None
    level: Optional[str] = None

class GenerateSkillsRequest(BaseModel):
    job_title: str
    years_of_experience: int

class SaveSkillsRequest(BaseModel):
    selected_skills: str  
    selected_language:str
    selected_level:str
class ProjectRequest(BaseModel):
   
    project_name: str
    link: Optional[str]=None
class ProjectDescriptionSaveRequest(BaseModel):
    
    project_name: str
    selected_description: str

# Certifications
class CertificationRequest(BaseModel):
    
    certification_title: str
    upload: Optional[str]=None
    link: Optional[str] = None 

class CertificationUpdateRequest(BaseModel):
    
    certification_title: Optional[str] = None
    upload: Optional[str] = None
    link: Optional[HttpUrl] = None

# Volunteering Experience
class VolunteeringRequest(BaseModel):
    organization: str
    role: str
    start_date: date
    end_date: Optional[date]
    description: Optional[str]=None

class GenerateVolunteeringRequest(BaseModel):
    volunteering_id: int


class SaveVolunteeringRequest(BaseModel):
    selected_description: str

# Awards
class AwardsRequest(BaseModel):
    award: str
    organization: Optional[str]
    start_date: date
    end_date: Optional[date]

# class ObjectiveRequest(BaseModel):
#     header_id: int
#     job_title: str
#     years_of_experience: int
#     selected_description: str


class ObjectiveSaveRequest(BaseModel):
    description: Optional[str] = None

# Template
class TemplateRequest(BaseModel):
    name: str
    structure: dict
    category: Optional[str] = None

