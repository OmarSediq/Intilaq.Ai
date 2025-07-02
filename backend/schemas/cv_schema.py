from pydantic import BaseModel, EmailStr,HttpUrl , ConfigDict
from typing import Optional
from datetime import date

class HeaderRequest(BaseModel):
    full_name: str
    job_title: Optional[str]=None
    email: EmailStr
    phone_number: Optional[str]=None
    address: Optional[str]=None
    linkedin_profile: Optional[str]=None
    github_profile: Optional[str]=None
    years_of_experience: Optional[int]=None


class HeaderResponse(BaseModel):
    full_name: str
    job_title: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
    linkedin_profile: Optional[str] = None
    github_profile: Optional[str] = None
    years_of_experience: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ExperienceRequest(BaseModel):

    role: str
    start_date: date
    end_date: Optional[date]
    company_name: Optional[str] = None

    @staticmethod
    def validate_dates(start_date: date, end_date: Optional[date]):
        if end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date")


class ExperienceResponse(BaseModel):
    id: int
    header_id: int
    role: str
    start_date: Optional[date]
    end_date: Optional[date]
    company_name: Optional[str]
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class ExperienceSaveRequest(BaseModel):

    selected_description: str


# Education
class EducationRequest(BaseModel):
    
    degree_and_major: str
    school: str
    city: Optional[str]
    country: Optional[str]
    start_date: date
    end_date: Optional[date]
    description: Optional[str] = None


class EducationResponse(BaseModel):
    id: int
    header_id: int
    degree_and_major: str
    school: str
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SkillsLanguagesRequest(BaseModel):
    languages: str  
    skills: Optional[str] = None
    level: Optional[str] = None


class SaveSkillsRequest(BaseModel):
    selected_skills: str  
    selected_language:str
    selected_level:str


class ProjectRequest(BaseModel):
   
    project_name: str
    link: Optional[str]=None

class ProjectResponse(BaseModel):
    id: int
    project_name: str
    link: Optional[str] = None
    description:Optional[str] = None
    class Config:
        from_attributes = True

class ProjectDescriptionSaveRequest(BaseModel):
    selected_description: str

class ProjectDescriptionSaveResponse(BaseModel):
    id: int
    project_name: str
    description: str
    class Config:
        from_attributes = True

# Certifications
class CertificationRequest(BaseModel):
    
    certification_title: str
    upload: Optional[str]=None
    link: Optional[str] = None 

class CertificationUpdateRequest(BaseModel):
    
    certification_title: Optional[str] = None
    upload: Optional[str] = None
    link: Optional[HttpUrl] = None


class CertResponse(BaseModel):
    id: int
    certification_title: str
    upload: Optional[str] = None
    link: Optional[str] = None
    class Config:
        from_attributes = True
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

class AwardResponse(BaseModel):
    id: int
    award: str
    organization: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    header_id: int

    class Config:
        from_attributes = True

class ObjectiveSaveRequest(BaseModel):
    description: Optional[str] = None

class ObjectiveResponse(BaseModel):
    id: int
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Template
class TemplateRequest(BaseModel):
    name: str
    structure: dict
    category: Optional[str] = None



# class GenerateSkillsRequest(BaseModel):
#     job_title: str
#     years_of_experience: int

# class ObjectiveRequest(BaseModel):
#     header_id: int
#     job_title: str
#     years_of_experience: int
#     selected_description: str

