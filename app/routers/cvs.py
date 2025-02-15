from fastapi import APIRouter, HTTPException, Depends,Response,Request
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import Date
from fastapi.responses import FileResponse
from app.dependencies import get_db 
from app.models import Header, Experience, Education, SkillsLanguages, Certifications, Projects, VolunteeringExperience, Awards, Objective
from pydantic import BaseModel, EmailStr,HttpUrl
from typing import Optional, List
from datetime import date
from sqlalchemy.future import select
from jinja2 import Template
from weasyprint import HTML,CSS
from app.services.mongo_services import add_template,update_template,delete_template,list_templates,get_template_by_id
from app.services.ai_services import generate_objective_from_ai,fetch_project_descriptions_from_ai,generate_experience_from_ai,generate_skills_from_ai,generate_volunteering_description_from_ai
from app.services.db_services import get_user_by_header_id
from app.config import env,TEMPLATES_DIR,PDF_DIR
import os
from datetime import datetime




router = APIRouter()

# --------------------- Models --------------------- #

# Header (Personal Information)
class HeaderRequest(BaseModel):
    full_name: str
    job_title: Optional[str] #  input for objective  
    email: EmailStr
    phone_number: Optional[str]
    address: Optional[str]
    linkedin_profile: Optional[str]
    github_profile: Optional[str]
    years_of_experience: Optional[int]  #  input for objective 

# Experience
# class ExperienceRequest(BaseModel):
#     header_id: int
#     role: str # input 
#     company_name: str
#     start_date: date # input 
#     end_date: Optional[date] # input 
#     description: Optional[str]  #  out ai 

class ExperienceRequest(BaseModel):
    header_id: int
    role: str
    start_date: date
    end_date: Optional[date]
    company_name: Optional[str] = None

    @staticmethod
    def validate_dates(start_date: date, end_date: Optional[date]):
        if end_date and start_date > end_date:
            raise ValueError("Start date cannot be after end date")

class ExperienceSaveRequest(BaseModel):
    header_id: int
    role: str
    selected_description: str


# Education
class EducationRequest(BaseModel):
    header_id: int
    degree_and_major: str
    school: str
    city: Optional[str]
    country: Optional[str]
    start_date: date
    end_date: Optional[date]
    description: Optional[str]

# Skills & Languages
# class SkillsLanguagesRequest(BaseModel):
#     header_id: int
#     skills: Optional[str] = None # out ai , input role and years from header 
#     languages: str  
#     level: Optional[str] 

class SkillsLanguagesRequest(BaseModel):
    languages: str  
    skills: Optional[str] = None
    level: Optional[str] = None

class GenerateSkillsRequest(BaseModel):
    header_id:int
    job_title: str
    years_of_experience: int

class SaveSkillsRequest(BaseModel):
    header_id: int
    selected_skills: str  
    selected_language:str
    selected_level:str


# # Projects
# class ProjectRequest(BaseModel):
#     header_id: int
#     project_name: str
#     description: Optional[str] # ai 
#     link: Optional[str]

class ProjectRequest(BaseModel):
    header_id: int
    project_name: str
    link: Optional[str]

class ProjectDescriptionSaveRequest(BaseModel):
    header_id: int
    project_name: str
    selected_description: str



# Certifications
class CertificationRequest(BaseModel):
    header_id: int
    certification_title: str
    upload: Optional[str]=None
    link: Optional[str] = None 

class CertificationUpdateRequest(BaseModel):
    certification_title: Optional[str] = None
    upload: Optional[str] = None
    link: Optional[HttpUrl] = None

# Volunteering Experience
class VolunteeringRequest(BaseModel):
    header_id: int
    organization: str
    role: str
    start_date: date
    end_date: Optional[date]
    description: Optional[str]=None

class GenerateVolunteeringRequest(BaseModel):
    volunteering_id: int


class SaveVolunteeringRequest(BaseModel):
    header_id: int
    selected_description: str

# Awards
class AwardsRequest(BaseModel):
    header_id: int
    award: str
    organization: Optional[str]
    start_date: date
    end_date: Optional[date]

# Objective
# class ObjectiveRequest(BaseModel):
#     header_id: int 
#     description:  str # ai 

class ObjectiveRequest(BaseModel):
    header_id: int
    job_title: str
    years_of_experience: int

class ObjectiveSaveRequest(BaseModel):
    header_id: int
    selected_description: str



# Template
class TemplateRequest(BaseModel):
    name: str
    structure: dict
    category: Optional[str] = None


# --------------------- Endpoints --------------------- #

# Header Endpoints
@router.post("/api/headers/")
async def create_header(request: HeaderRequest, db: AsyncSession = Depends(get_db)):
    header = Header(**request.dict())
    db.add(header)
    await db.commit()
    await db.refresh(header)
    return {"message": "Header created successfully", "data": header}

@router.get("/api/headers/{header_id}/")
async def get_header(header_id: int, db: AsyncSession = Depends(get_db)):
    header = await db.get(Header, header_id)
    if not header:
        raise HTTPException(status_code=404, detail="Header not found")
    return {"data": header}

@router.put("/api/headers/{header_id}/")
async def update_header(header_id: int, request: HeaderRequest, db: AsyncSession = Depends(get_db)):
    header = await db.get(Header, header_id)
    if not header:
        raise HTTPException(status_code=404, detail="Header not found")
    for key, value in request.dict(exclude_unset=True).items():
        setattr(header, key, value)
    await db.commit()
    await db.refresh(header)
    return {"message": "Header updated successfully", "data": header}

@router.delete("/api/headers/{header_id}/")
async def delete_header(header_id: int, db: AsyncSession = Depends(get_db)):
    header = await db.get(Header, header_id)
    if not header:
        raise HTTPException(status_code=404, detail="Header not found")
    await db.delete(header)
    await db.commit()
    return {"message": "Header deleted successfully"}

# Experience Endpoints
@router.post("/api/experiences/")
async def create_experience(request: ExperienceRequest, db: AsyncSession = Depends(get_db)):
    ExperienceRequest.validate_dates(request.start_date, request.end_date)
    experience = Experience(**request.dict())
    db.add(experience)
    await db.flush()  
    await db.commit()
    await db.refresh(experience)
    return {"message": "Experience created successfully", "data": experience}

@router.get("/api/experiences/{experience_id}/")
async def get_experience(experience_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Experience).where(Experience.id == experience_id)
    result = await db.execute(stmt)
    experience = result.scalars().first()

    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    return {"data": experience}

@router.put("/api/experiences/{experience_id}/")
async def update_experience(experience_id: int, request: ExperienceRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Experience).where(Experience.id == experience_id)
    result = await db.execute(stmt)
    experience = result.scalars().first()

    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")

    request.validate_dates(request.start_date, request.end_date)
    for key, value in request.dict(exclude_unset=True).items():
        setattr(experience, key, value)
    await db.commit()
    await db.refresh(experience)
    return {"message": "Experience updated successfully", "data": experience}

@router.delete("/api/experiences/{experience_id}/")
async def delete_experience(experience_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Experience).where(Experience.id == experience_id)
    result = await db.execute(stmt)
    experience = result.scalars().first()

    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")

    await db.delete(experience)
    await db.commit()
    return {"message": "Experience deleted successfully"}

# Education Endpoints
@router.post("/api/educations/")
async def create_education(request: EducationRequest, db: AsyncSession = Depends(get_db)):
    education = Education(**request.dict())
    db.add(education)
    await db.commit()
    await db.refresh(education)
    return {"message": "Education created successfully", "data": education}

@router.get("/api/educations/{education_id}/")
async def get_education(education_id: int, db: AsyncSession = Depends(get_db)):
    education = await db.get(Education, education_id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    return {"data": education}

@router.put("/api/educations/{education_id}/")
async def update_education(education_id: int, request: EducationRequest, db: AsyncSession = Depends(get_db)):
    education = await db.get(Education, education_id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    for key, value in request.dict(exclude_unset=True).items():
        setattr(education, key, value)
    await db.commit()
    await db.refresh(education)
    return {"message": "Education updated successfully", "data": education}

@router.delete("/api/educations/{education_id}/")
async def delete_education(education_id: int, db: AsyncSession = Depends(get_db)):
    education = await db.get(Education, education_id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    await db.delete(education)
    await db.commit()
    return {"message": "Education deleted successfully"}
@router.post("/api/skills-languages/")
async def create_skills_languages(request: SkillsLanguagesRequest, db: AsyncSession = Depends(get_db)):
    """Create a new Skills & Languages entry (POST)."""

    if not request.skills:
        request.skills = "Default Skill"  
    skills_languages = SkillsLanguages(**request.dict())
    db.add(skills_languages)
    await db.commit()
    await db.refresh(skills_languages)
    
    return {"message": "Skills & Languages created successfully", "data": skills_languages}


@router.get("/api/skills-languages/{skills_id}/")
async def get_skills_languages(skills_id: int, db: AsyncSession = Depends(get_db)):
    """Get Skills & Languages by ID (GET)."""
    skills_languages = await db.get(SkillsLanguages, skills_id)
    if not skills_languages:
        raise HTTPException(status_code=404, detail="Skills & Languages not found")
    return {"data": skills_languages}


@router.delete("/api/skills-languages/{skills_id}/")
async def delete_skills_languages(skills_id: int, db: AsyncSession = Depends(get_db)):
    """Delete Skills & Languages entry (DELETE)."""
    skills_languages = await db.get(SkillsLanguages, skills_id)
    if not skills_languages:
        raise HTTPException(status_code=404, detail="Skills & Languages not found")
    
    await db.delete(skills_languages)
    await db.commit()
    
    return {"message": "Skills & Languages deleted successfully"}


@router.post("/api/projects/")
async def create_project(request: ProjectRequest, db: AsyncSession = Depends(get_db)):
    try:
        project = Projects(**request.dict(exclude_none=True))
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return {"message": "Project created successfully", "data": project}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/api/projects/{project_id}/")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get project by ID (GET)."""
    project = await db.get(Projects, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"data": project}

@router.put("/api/projects/{project_id}/")
async def update_project(project_id: int, request: ProjectRequest, db: AsyncSession = Depends(get_db)):
    """Update a project (PUT)."""
    project = await db.get(Projects, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in request.dict(exclude_unset=True).items():
        setattr(project, key, value)
    await db.commit()
    await db.refresh(project)
    return {"message": "Project updated successfully", "data": project}

@router.delete("/api/projects/{project_id}/")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a project (DELETE)."""
    project = await db.get(Projects, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted successfully"}

@router.post("/api/certifications/")
async def create_certification(request: CertificationRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new certification entry.
    """
    certification = Certifications(**request.dict(exclude_unset=True))  # تجاهل الحقول غير المرسلة
    db.add(certification)
    await db.commit()
    await db.refresh(certification)

    return {"message": "Certification created successfully", "data": certification}
@router.put("/api/certifications/{certification_id}/")
async def update_certification(certification_id: int, request: CertificationUpdateRequest, db: AsyncSession = Depends(get_db)):
    """
    Update an existing certification.
    """
    certification = await db.get(Certifications, certification_id)

    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")

    update_data = request.dict(exclude_unset=True)
    if "link" in update_data and update_data["link"] is not None:
        update_data["link"] = str(update_data["link"])

    for key, value in update_data.items():
        setattr(certification, key, value)

    await db.commit()
    await db.refresh(certification)

    return {"message": "Certification updated successfully", "data": certification}


@router.get("/api/certifications/{certification_id}/")
async def get_certification(certification_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get certification by ID (GET).
    """
    certification = await db.get(Certifications, certification_id)
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    return {"data": certification}

@router.delete("/api/certifications/{certification_id}/")
async def delete_certification(certification_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a certification (DELETE).
    """
    certification = await db.get(Certifications, certification_id)
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")

    await db.delete(certification)
    await db.commit()

    return {"message": "Certification deleted successfully"}
@router.post("/api/volunteerings/")
async def create_volunteering(request: VolunteeringRequest, db: AsyncSession = Depends(get_db)):
    """Create a new volunteering experience (POST)."""
    volunteering = VolunteeringExperience(**request.dict())
    db.add(volunteering)
    await db.commit()
    await db.refresh(volunteering)
    return {"message": "Volunteering experience created successfully", "data": volunteering}

@router.get("/api/volunteerings/{volunteering_id}/")
async def get_volunteering(volunteering_id: int, db: AsyncSession = Depends(get_db)):
    """Get volunteering experience by ID (GET)."""
    volunteering = await db.get(VolunteeringExperience, volunteering_id)
    if not volunteering:
        raise HTTPException(status_code=404, detail="Volunteering experience not found")
    return {"data": volunteering}

@router.delete("/api/volunteerings/{volunteering_id}/")
async def delete_volunteering(volunteering_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a volunteering experience (DELETE)."""
    volunteering = await db.get(VolunteeringExperience, volunteering_id)
    if not volunteering:
        raise HTTPException(status_code=404, detail="Volunteering experience not found")
    await db.delete(volunteering)
    await db.commit()
    return {"message": "Volunteering experience deleted successfully"}

@router.post("/api/volunteerings-suggestions/")
async def generate_volunteering_suggestions(request: GenerateVolunteeringRequest, db: AsyncSession = Depends(get_db)):
    """
    Generate AI-based volunteering descriptions based on role.
    """
    try:
        volunteering = await db.get(VolunteeringExperience, request.volunteering_id)
        if not volunteering:
            raise HTTPException(status_code=404, detail="Volunteering experience not found")

        ai_suggestions = await generate_volunteering_description_from_ai(volunteering.role)
        
        return {
            "message": "AI suggestions generated successfully",
            "suggestions": ai_suggestions
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/api/volunteerings-save-description/{volunteering_id}")
async def save_volunteering_description(
    volunteering_id: int, request: SaveVolunteeringRequest, db: AsyncSession = Depends(get_db)
):
    """
    Save the selected volunteering description to the database.
    """
    try:
        volunteering = await db.get(VolunteeringExperience, volunteering_id)
        if not volunteering:
            raise HTTPException(status_code=404, detail="Volunteering experience not found")

        if volunteering.header_id != request.header_id:
            raise HTTPException(
                status_code=400,
                detail="Provided header_id does not match the existing volunteering record",
            )

        volunteering.description = request.selected_description
        await db.commit()

        return {"message": "Volunteering description updated successfully", "data": request.selected_description}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating volunteering description: {str(e)}")



@router.post("/api/awards/")
async def create_award(request: AwardsRequest, db: AsyncSession = Depends(get_db)):
    """Create a new award (POST)."""
    award = Awards(**request.dict())
    db.add(award)
    await db.commit()
    await db.refresh(award)
    return {"message": "Award created successfully", "data": award}

@router.get("/api/awards/{award_id}/")
async def get_award(award_id: int, db: AsyncSession = Depends(get_db)):
    """Get award by ID (GET)."""
    award = await db.get(Awards, award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")
    return {"data": award}

@router.delete("/api/awards/{award_id}/")
async def delete_award(award_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an award (DELETE)."""
    award = await db.get(Awards, award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")
    await db.delete(award)
    await db.commit()
    return {"message": "Award deleted successfully"}
# @router.post("/objectives/")
# async def create_objective(request: ObjectiveRequest, db: AsyncSession = Depends(get_db)):
#     """Create a new objective (POST)."""
#     objective = Objective(**request.dict())
#     db.add(objective)
#     await db.commit()
#     await db.refresh(objective)
#     return {"message": "Objective created successfully", "data": objective}

# @router.get("/objectives/{objective_id}/") # from AI 
# async def get_objective(objective_id: int, db: AsyncSession = Depends(get_db)):
#     """Get objective by ID (GET)."""
#     objective = await db.get(Objective, objective_id)
#     if not objective:
#         raise HTTPException(status_code=404, detail="Objective not found")
#     return {"data": objective}

# @router.delete("/objectives/{objective_id}/")
# async def delete_objective(objective_id: int, db: AsyncSession = Depends(get_db)):
#     """Delete an objective (DELETE)."""
#     objective = await db.get(Objective, objective_id)
#     if not objective:
#         raise HTTPException(status_code=404, detail="Objective not found")
#     await db.delete(objective)
#     await db.commit()
#     return {"message": "Objective deleted successfully"}




@router.post("/api/templates/")
async def create_template(request: TemplateRequest):
    try:
        template = await add_template(request.dict())
        return {"message": "Template added successfully", "data": template}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding template: {e}")

@router.get("/api/templates/{template_id}/")
async def read_template(template_id: str):
    template = await get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"data": template}

@router.get("/api/templates/")
async def read_templates():
    try:
        templates = await list_templates()
        return {"data": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {e}")

@router.put("/api/templates/{template_id}/")
async def update_template_endpoint(template_id: str, request: TemplateRequest):
    updated_template = await update_template(template_id, request.dict())
    if not updated_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template updated successfully", "data": updated_template}

@router.delete("/api/templates/{template_id}/")
async def delete_template_endpoint(template_id: str):
    success = await delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

def safe_get(data, key, default=""):
    return data.get(key, default) if data.get(key) is not None else default


@router.get("/api/generate-cv/{header_id}")
async def generate_cv(header_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user_data = await get_user_by_header_id(db, header_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    print("User data fetched successfully.")
    
    template_path = os.path.join(TEMPLATES_DIR, "resume_template.html")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail=f"Template not found at: {template_path}")
    
    try:
        template = env.get_template("resume_template.html")
    except Exception as e:
        print(f"Error loading template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template error: {str(e)}")
    
    def format_date(date_str):
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %Y")
            except ValueError:
                return date_str
        return "Present"

    try:
        html_content = template.render(
            full_name=safe_get(user_data, "full_name"),
            job_title=safe_get(user_data, "job_title"),
            email=safe_get(user_data, "email"),
            phone_number=safe_get(user_data, "phone_number"),
            address=safe_get(user_data, "address"),
            years_of_experience=safe_get(user_data, "years_of_experience"),
            github_profile=safe_get(user_data, "github_profile"),
            linkedin_profile=safe_get(user_data, "linkedin_profile"),
            objective=safe_get(user_data, "objective"),
            education=[{**edu, "start_date": format_date(edu["start_date"]), "end_date": format_date(edu.get("end_date"))} for edu in safe_get(user_data, "education", [])],
            experience=[{**exp, "start_date": format_date(exp["start_date"]), "end_date": format_date(exp.get("end_date"))} for exp in safe_get(user_data, "experience", [])],
            skills_languages=safe_get(user_data, "skills_languages", []),
            certifications=safe_get(user_data, "certifications", []),
            projects=safe_get(user_data, "projects", []),
            volunteering_experience=[{**vol, "start_date": format_date(vol["start_date"]), "end_date": format_date(vol.get("end_date"))} for vol in safe_get(user_data, "volunteering_experience", [])],
            awards=[{**award, "start_date": format_date(award["start_date"]), "end_date": format_date(award.get("end_date"))} for award in safe_get(user_data, "awards", [])]
        )
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error rendering template: {str(e)}")

    print("HTML content generated.")

    filename = f"{user_data.get('full_name', 'Generated_CV')}_CV.pdf".replace(" ", "_")
    pdf_path = os.path.join(PDF_DIR, filename)

    try:
        HTML(string=html_content).write_pdf(pdf_path)
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
    
    print(f"PDF generated successfully: {pdf_path}")

    base_url = str(request.base_url).rstrip("/")
    download_link = f"{base_url}/api/download-cv/{filename}"

    return {"message": "CV generated successfully!", "download_link": download_link}


@router.get("/api/download-cv/{filename}")
async def download_cv(filename: str):
    """
    Download the generated CV PDF.
    """
    file_path = os.path.join("generated_pdfs", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    print("✅ Serving file:", file_path)
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

@router.post("/api/objectives/suggestions/")
async def generate_objective_suggestions(request: ObjectiveRequest, db: AsyncSession = Depends(get_db)):
    try:
      
        db_objective = Objective(
            header_id=request.header_id,
            description=""  
        )
        db.add(db_objective)
        await db.commit()
        await  db.refresh(db_objective)  

       
        ai_suggestions = await generate_objective_from_ai(
            job_title=request.job_title,
            years_of_experience=request.years_of_experience
        )

        return {
            "message": "AI suggestions generated successfully",
            "objective_id": db_objective.id,  
            "header_id": request.header_id,
            "suggestions": ai_suggestions
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()  
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/api/objectives/save-description/{objective_id}")
async def save_objective_description(objective_id: int, request: ObjectiveSaveRequest, db: AsyncSession = Depends(get_db)):
    """
    Save the selected objective description to the database.
    """
    objective = await db.get(Objective, objective_id)

    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")

    objective.description = request.selected_description

    await db.commit()
    await db.refresh(objective)

    return {"message": "Objective description updated successfully", "data": {"objective_id": objective_id, "description": request.selected_description}}

@router.post("/api/projects/generate-description/")
async def generate_project_description(request: ProjectRequest):
    """
    Generate project descriptions from the external AI API.
    """
    try:
        ai_suggestions = await fetch_project_descriptions_from_ai(
            project_name=request.project_name
        )
        return {
            "message": "AI suggestions generated successfully",
            "suggestions": ai_suggestions
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/api/projects/save-description/{project_id}")
async def save_project_description(
    project_id: int, request: ProjectDescriptionSaveRequest, db: AsyncSession = Depends(get_db)
):
    """
    Save the selected project description to the database using ProjectDescriptionSaveRequest.
    """
    try:
        project = await db.get(Projects, project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.header_id != request.header_id or project.project_name != request.project_name:
            raise HTTPException(
                status_code=400,
                detail="Provided header_id or project_name does not match the existing project record",
            )

        project.description = request.selected_description

        await db.commit()

        return {"message": "Project description updated successfully", "data": request.selected_description}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project description: {str(e)}")

@router.post("/api/experiences/suggestions/")
async def generate_experience_suggestions(request: ExperienceRequest):
    """
    Generate AI-based suggestions for experience description.
    """
    try:
        ai_suggestions = await generate_experience_from_ai(
            role=request.role,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {
            "message": "AI suggestions generated successfully",
            "suggestions": ai_suggestions
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/api/experiences/save-description/{experience_id}")
async def save_experience_description(
    experience_id: int, request: ExperienceSaveRequest, db: AsyncSession = Depends(get_db)
):
    """
    Save selected experience description to the database using ExperienceSaveRequest.
    """
    try:
        experience = await db.get(Experience, experience_id)

        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        if experience.header_id != request.header_id or experience.role != request.role:
            raise HTTPException(
                status_code=400,
                detail="Provided header_id or role does not match the existing experience record",
            )

        experience.description = request.selected_description

        await db.commit()

        return {"message": "Experience description updated successfully", "data": request.selected_description}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating experience description: {str(e)}")
    
@router.post("/api/skills/suggestions/")
async def generate_skills_suggestions(request: GenerateSkillsRequest, db: AsyncSession = Depends(get_db)):
    """
    Generate AI-based suggestions for skills based on job title and years of experience using Google Gemini AI.
    """
    try:
        db_skills_languages = SkillsLanguages(  
            header_id=request.header_id,
            skills="",  
            languages="",
            level=None  
        )
        db.add(db_skills_languages)
        await db.commit()
        await db.refresh(db_skills_languages)

        ai_suggestions = await generate_skills_from_ai(
            job_title=request.job_title,
            years_of_experience=request.years_of_experience
        )

        return {
            "message": "AI suggestions generated successfully",
            "suggestions": ai_suggestions
        }
    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/api/skills/save/{skills_id}")
async def save_skills(
    skills_id: int, request: SaveSkillsRequest, db: AsyncSession = Depends(get_db)
):
    """
    Save the selected skills, languages, and level to the database using SaveSkillsRequest.
    """
    try:
        skills_record = await db.get(SkillsLanguages, skills_id)

        if not skills_record:
            raise HTTPException(status_code=404, detail="Skills record not found")

        if skills_record.header_id != request.header_id:
            raise HTTPException(
                status_code=400,
                detail="Provided header_id does not match the existing skills record",
            )

        skills_record.skills = request.selected_skills
        skills_record.languages = request.selected_language  
        skills_record.level = request.selected_level  

        await db.commit()
        await db.refresh(skills_record) 

        return {
            "message": "Skills updated successfully",
            "data": {
                "skills": skills_record.skills,
                "languages": skills_record.languages,
                "level": skills_record.level
            }
        }

    except Exception as e:
        await db.rollback()  
        raise HTTPException(status_code=500, detail=f"Error updating skills: {str(e)}")
