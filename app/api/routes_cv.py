# from fastapi import APIRouter, Depends,status
# from sqlalchemy.ext.asyncio import AsyncSession 
# from app.core.dependencies import get_db 
# from app.database.models import Header, Experience, Education, SkillsLanguages, Certifications, Projects, VolunteeringExperience, Awards, Objective
# from sqlalchemy.future import select
# from weasyprint import HTML,CSS
# from app.schemas.cv import HeaderRequest,ExperienceRequest,EducationRequest,ProjectDescriptionSaveRequest,ProjectRequest,ObjectiveSaveRequest,VolunteeringRequest,SaveVolunteeringRequest,GenerateSkillsRequest,GenerateVolunteeringRequest,SkillsLanguagesRequest,ExperienceSaveRequest,CertificationRequest,CertificationUpdateRequest,AwardsRequest,SaveSkillsRequest
# from app.services.ai_services import generate_objective_from_ai,fetch_project_descriptions_from_ai,generate_experience_from_ai,generate_skills_from_ai,generate_volunteering_description_from_ai
# from app.database.db_services import get_user_by_header_id,generate_docx_from_html
# from app.core.config import env
# from fastapi.responses import StreamingResponse, HTMLResponse
# from app.utils.response_schemas import error_response,success_response,serialize_sqlalchemy_object
# from app.api.routes_auth import get_current_user
# import io
# import pdfkit
# from sqlalchemy import select


# router = APIRouter()

# # --------------------- Models --------------------- #
# config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
# # Header (Personal Information)

# # --------------------- Endpoints --------------------- #

# # Header Endpoints

# # Experience Endpoints
# @router.post("/api/experiences/", tags=["Experience Management"])
# async def create_experience(
#     request: ExperienceRequest, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(
#         select(Header).where(Header.user_id == int(user["user_id"]))
#     )
#     header = result.scalars().first()

#     if not header:
#         return error_response(code=404, error_message="Header not found for this user.")

#     ExperienceRequest.validate_dates(request.start_date, request.end_date)

#     experience = Experience(**request.dict(exclude={"header_id"}), header_id=header.id)

#     db.add(experience)
#     await db.commit()
#     await db.refresh(experience)

#     return success_response(code=201, data={
#         "message": "Experience created successfully",
#         "experience": serialize_sqlalchemy_object(experience)
#     })

# @router.get("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def get_experience(
#     experience_id: int, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):

#     stmt = select(Experience).where(Experience.id == experience_id)
#     result = await db.execute(stmt)
#     experience = result.scalars().first()

#     if not experience:
#         return error_response(code=404, error_message="Experience not found")

#     header = await db.get(Header, experience.header_id)
#     if not header or header.user_id != int(user["user_id"]):
#         return error_response(code=403, error_message="Unauthorized access to this experience")

#     return success_response(code=200, data={"experience":serialize_sqlalchemy_object(experience)})

# @router.put("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def update_experience(
#     experience_id: int, 
#     request: ExperienceRequest, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     stmt = select(Experience).where(Experience.id == experience_id)
#     result = await db.execute(stmt)
#     experience = result.scalars().first()
#     if not experience:
#         return error_response(code=404, error_message="Experience not found")

#     header = await db.get(Header, experience.header_id)
#     if not header or header.user_id != int(user["user_id"]):
#         return error_response(code=403, error_message="Unauthorized access to this experience")

#     request.validate_dates(request.start_date, request.end_date)

#     for key, value in request.dict(exclude_unset=True).items():
#         setattr(experience, key, value)

#     await db.commit()
#     await db.refresh(experience)
#     return success_response(code=200, data={"message": "Experience updated successfully", "experience": serialize_sqlalchemy_object(experience)})

# @router.delete("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def delete_experience(
#     experience_id: int, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     stmt = select(Experience).where(Experience.id == experience_id)
#     result = await db.execute(stmt)
#     experience = result.scalars().first()

#     if not experience:
#         return error_response(code=404, error_message="Experience not found")

#     header = await db.get(Header, experience.header_id)
#     if not header or header.user_id != int(user["user_id"]):
#         return error_response(code=403, error_message="Unauthorized access to this experience")

#     await db.delete(experience)
#     await db.commit()
    
#     return success_response(code=200, data={"message": "Experience deleted successfully"})

# # Education Endpoints
# @router.post("/api/educations/", tags=["Education Management"])
# async def create_education(
#     request: EducationRequest, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(
#         select(Header).where(Header.user_id == int(user["user_id"]))
#     )
#     header = result.scalars().first()

#     if not header:
#         return error_response(code=404, error_message="Header not found for this user.")

#     education = Education(**request.dict(exclude={"header_id"}), header_id=header.id)
#     db.add(education)
#     await db.commit()
#     await db.refresh(education)
    
#     return success_response(code=201, data={
#         "message": "Education created successfully",
#         "education": serialize_sqlalchemy_object(education)
#     })

# @router.get("/api/educations/{education_id}/", tags=["Education Management"])
# async def get_education(
#     education_id: int, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
 
#     education = await db.get(Education, education_id)

#     if not education:
#         return error_response(code=404, error_message="Education not found")

#     header = await db.get(Header, education.header_id)
#     if not header or header.user_id != int(user["user_id"]):
#         return error_response(code=403, error_message="Unauthorized access to this education")

#     return success_response(code=200, data={"education": serialize_sqlalchemy_object(education)})

# @router.put("/api/educations/{education_id}/", tags=["Education Management"])
# async def update_education(
#     education_id: int, 
#     request: EducationRequest, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     education = await db.get(Education, education_id)

#     if not education:
#         return error_response(code=404, error_message="Education not found")

#     header = await db.get(Header, education.header_id)
#     if not header or header.user_id != int(user["user_id"]):
#         return error_response(code=403, error_message="Unauthorized access to this education")

#     for key, value in request.dict(exclude_unset=True).items():
#         setattr(education, key, value)
#     await db.commit()
#     await db.refresh(education)
    
#     return success_response(code=200, data={"message": "Education updated successfully", "education": serialize_sqlalchemy_object(education)})

# @router.delete("/api/educations/{education_id}/", tags=["Education Management"])
# async def delete_education(
#     education_id: int, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     education = await db.get(Education, education_id)

#     if not education:
#         return error_response(code=404, error_message="Education not found")

#     header = await db.get(Header, education.header_id)
#     if not header or header.user_id != int(user["user_id"]):
#         return error_response(code=403, error_message="Unauthorized access to this education")

#     await db.delete(education)
#     await db.commit()
#     return success_response(code=200, data={"message": "Education deleted successfully"})

# @router.post("/api/skills-languages/", tags=["Skills & Languages"])
# async def create_skills_languages(
#     request: SkillsLanguagesRequest, 
#     user: dict = Depends(get_current_user),  
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         skills_languages = SkillsLanguages(
#             header_id=header.id,
#             skills=request.skills,
#             languages=request.languages,
#             level=request.level
#         )
#         db.add(skills_languages)
#         await db.commit()
#         await db.refresh(skills_languages)

#         return success_response(code=201, data={
#             "id": skills_languages.id,
#             "header_id": skills_languages.header_id,
#             "skills": skills_languages.skills,
#             "languages": skills_languages.languages,
#             "level": skills_languages.level
#         }, message="Skills & Languages created successfully")

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


# @router.get("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
# async def get_skills_languages(
#     skills_id: int, 
#     user: dict = Depends(get_current_user),  
#     db: AsyncSession = Depends(get_db)
# ):

#     try:
#         skills_languages = await db.get(SkillsLanguages, skills_id)
#         if not skills_languages:
#             return error_response(code=404, error_message="Skills & Languages not found")
        
#         header = await db.get(Header, skills_languages.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to view this resource.")

#         return success_response(code=200, data={
#             "id": skills_languages.id,
#             "header_id": skills_languages.header_id,
#             "skills": skills_languages.skills,
#             "languages": skills_languages.languages,
#             "level": skills_languages.level
#         }, message="Skills & Languages retrieved successfully")

#     except Exception as e:
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))



# @router.delete("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
# async def delete_skills_languages(
#     skills_id: int, 
#     user: dict = Depends(get_current_user),  
#     db: AsyncSession = Depends(get_db)
# ):
  
#     try:
#         skills_languages = await db.get(SkillsLanguages, skills_id)
#         if not skills_languages:
#             return error_response(code=404, error_message="Skills & Languages not found")
        
#         header = await db.get(Header, skills_languages.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to delete this resource.")

#         await db.delete(skills_languages)
#         await db.commit()
#         return success_response(code=200, data={"message": "Skills & Languages deleted successfully"})

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))
    
# @router.post("/api/projects/", tags=["Projects & Certifications"])
# async def create_project(
#     request: ProjectRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         project = Projects(**request.dict(exclude={"header_id"}), header_id=header.id)
        
#         db.add(project)
#         await db.commit()
#         await db.refresh(project)

#         return success_response(code=201, data={
#             "message": "Project created successfully",
#             "data": serialize_sqlalchemy_object(project)
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))



# @router.get("/api/projects/{project_id}/", tags=["Projects & Certifications"])
# async def get_project(
#     project_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
    
#     try:
#         project = await db.get(Projects, project_id)
#         if not project:
#             return error_response(code=404, error_message="Project not found")

#         header = await db.get(Header, project.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to view this project.")

#         return success_response(code=200, data={"data": serialize_sqlalchemy_object(project)})

#     except Exception as e:
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))

# @router.put("/api/projects/{project_id}/", tags=["Projects & Certifications"])
# async def update_project(
#     project_id: int,
#     request: ProjectRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):

#     try:
#         project = await db.get(Projects, project_id)
#         if not project:
#             return error_response(code=404, error_message="Project not found")

#         header = await db.get(Header, project.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to update this project.")

#         for key, value in request.dict(exclude_unset=True).items():
#             setattr(project, key, value)

#         await db.commit()
#         await db.refresh(project)

#         return success_response(code=200, data={"message": "Project updated successfully", "data": serialize_sqlalchemy_object(project)})

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))

# @router.delete("/api/projects/{project_id}/", tags=["Projects & Certifications"])
# async def delete_project(
#     project_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
    
#     try:
#         project = await db.get(Projects, project_id)
#         if not project:
#             return error_response(code=404, error_message="Project not found")

#         header = await db.get(Header, project.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to delete this project.")

#         await db.delete(project)
#         await db.commit()

#         return success_response(code=200, data={"message": "Project deleted successfully"})

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))
# @router.post("/api/certifications/", tags=["Projects & Certifications"])
# async def create_certification(
#     request: CertificationRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         certification = Certifications(
#             **request.dict(exclude={"header_id"}),
#             header_id=header.id
#         )
        
#         db.add(certification)
#         await db.commit()
#         await db.refresh(certification)

#         return success_response(
#             code=201,
#             data={
#                 "message": "Certification created successfully",
#                 "data": serialize_sqlalchemy_object(certification)
#             }
#         )

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


# @router.put("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def update_certification(
#     certification_id: int,
#     request: CertificationUpdateRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         certification = await db.get(Certifications, certification_id)
#         if not certification:
#             return error_response(code=404, error_message="Certification not found")

#         header = await db.get(Header, certification.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to update this certification.")

#         update_data = request.dict(exclude_unset=True)
#         if "link" in update_data and update_data["link"] is not None:
#             update_data["link"] = str(update_data["link"])

#         for key, value in update_data.items():
#             setattr(certification, key, value)

#         await db.commit()
#         await db.refresh(certification)

#         return success_response(code=200, data={"message": "Certification updated successfully", "data": serialize_sqlalchemy_object(certification)})

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))

# @router.get("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def get_certification(
#     certification_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         certification = await db.get(Certifications, certification_id)
#         if not certification:
#             return error_response(code=404, error_message="Certification not found")

#         header = await db.get(Header, certification.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to view this certification.")

#         return success_response(code=200, data={"data": serialize_sqlalchemy_object(certification)})

#     except Exception as e:
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))



# @router.delete("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def delete_certification(
#     certification_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         certification = await db.get(Certifications, certification_id)
#         if not certification:
#             return error_response(code=404, error_message="Certification not found")

#         header = await db.get(Header, certification.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to delete this certification.")

#         await db.delete(certification)
#         await db.commit()

#         return success_response(code=200, data={"message": "Certification deleted successfully"})

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))
    
# @router.post("/api/volunteerings/", tags=["Volunteering & Awards"])
# async def create_volunteering(
#     request: VolunteeringRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         volunteering = VolunteeringExperience(
#             **request.dict(exclude={"header_id"}),
#             header_id=header.id
#         )

#         db.add(volunteering)
#         await db.commit()
#         await db.refresh(volunteering)

#         return success_response(
#             code=201,
#             data={
#                 "message": "Volunteering experience created successfully",
#                 "data": serialize_sqlalchemy_object(volunteering)
#             }
#         )

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message=f"Unexpected error: {str(e)}")



# @router.get("/api/volunteerings/{volunteering_id}/", tags=["Volunteering & Awards"])
# async def get_volunteering(
#     volunteering_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         volunteering = await db.get(VolunteeringExperience, volunteering_id)
#         if not volunteering:
#             return error_response(code=404, error_message="Volunteering experience not found")

#         header = await db.get(Header, volunteering.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to view this volunteering experience.")

#         return success_response(code=200, data={"data": serialize_sqlalchemy_object(volunteering)})

#     except Exception as e:
#         return error_response(code=500, error_message=f"Unexpected error: {str(e)}")

        

# @router.delete("/api/volunteerings/{volunteering_id}/", tags=["Volunteering & Awards"])
# async def delete_volunteering(
#     volunteering_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         volunteering = await db.get(VolunteeringExperience, volunteering_id)
#         if not volunteering:
#             return error_response(code=404, error_message="Volunteering experience not found")

#         header = await db.get(Header, volunteering.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to delete this volunteering experience.")

#         await db.delete(volunteering)
#         await db.commit()

#         return success_response(code=200, data={"message": "Volunteering experience deleted successfully"})

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message=f"Unexpected error: {str(e)}")



# @router.post("/api/volunteerings-suggestions/", tags=["AI Enhancements"])
# async def generate_volunteering_suggestions(
#     request: GenerateVolunteeringRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         volunteering = await db.get(VolunteeringExperience, request.volunteering_id)
#         if not volunteering:
#             return error_response(code=404, error_message="Volunteering experience not found")

#         header = await db.get(Header, volunteering.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to generate AI suggestions for this volunteering experience.")

#         ai_suggestions = await generate_volunteering_description_from_ai(volunteering.role)

#         return success_response(code=200, data={"message": "AI suggestions generated successfully", "suggestions": serialize_sqlalchemy_object(ai_suggestions)})

#     except Exception as e:
#         return error_response(code=500, error_message=f"Unexpected error: {str(e)}")

# @router.put("/api/volunteerings-save-description/{volunteering_id}/", tags=["AI Enhancements"])
# async def save_volunteering_description(
#     volunteering_id: int,
#     request: SaveVolunteeringRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         volunteering = await db.get(VolunteeringExperience, volunteering_id)
#         if not volunteering:
#             return error_response(code=404, error_message="Volunteering experience not found")

#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         if volunteering.header_id != header.id:
#             return error_response(code=403, error_message="Unauthorized access to this volunteering experience.")

#         volunteering.description = request.selected_description
#         await db.commit()
#         await db.refresh(volunteering)

#         return success_response(code=200, data={
#             "message": "Volunteering description updated successfully",
#             "description": volunteering.description
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message=f"Error updating volunteering description: {str(e)}")
    
# @router.post("/api/awards/", tags=["Volunteering & Awards"])
# async def create_award(
#     request: AwardsRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         award = Awards(
#             **request.dict(exclude={"header_id"}),
#             header_id=header.id
#         )

#         db.add(award)
#         await db.commit()
#         await db.refresh(award)

#         return success_response(code=201, data={
#             "message": "Award created successfully",
#             "data": serialize_sqlalchemy_object(award)
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message=f"Unexpected error: {str(e)}")


# @router.get("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
# async def get_award(
#     award_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         award = await db.get(Awards, award_id)
#         if not award:
#             return error_response(code=404, error_message="Award not found")

#         header = await db.get(Header, award.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to access this award.")

#         return success_response(code=200, data={"data": serialize_sqlalchemy_object(award)})

#     except Exception as e:
#         return error_response(code=500, error_message=f"Unexpected error: {str(e)}")



# @router.delete("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
# async def delete_award(
#     award_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):

#     try:
#         award = await db.get(Awards, award_id)
#         if not award:
#             return error_response(code=404, error_message="Award not found")

#         header = await db.get(Header, award.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="You do not have permission to delete this award.")

#         await db.delete(award)
#         await db.commit()
#         return success_response(code=200, data={"message": "Award deleted successfully"})

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message=f"Unexpected error: {str(e)}")

# def safe_get(data, key, default=""):
#     return data.get(key, default) if data.get(key) is not None else default


# @router.get("/api/generate-cv/{header_id}/", response_class=HTMLResponse, tags=["CV Exporting"])
# async def generate_cv(header_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
#     try:
#         user_id = int(user["user_id"])
#         user_data = await get_user_by_header_id(db, header_id)

#         if not user_data or user_data["user_id"] != user_id:
#             return error_response(code=403, error_message="You do not have permission to access this CV.")

#         template = env.get_template("resume_template.html")
#         html_content = template.render(
#             full_name=safe_get(user_data, "full_name"),
#             job_title=safe_get(user_data, "job_title"),
#             email=safe_get(user_data, "email"),
#             phone_number=safe_get(user_data, "phone_number"),
#             address=safe_get(user_data, "address"),
#             years_of_experience=safe_get(user_data, "years_of_experience"),
#             github_profile=safe_get(user_data, "github_profile"),
#             linkedin_profile=safe_get(user_data, "linkedin_profile"),
#             objective=safe_get(user_data, "objective"),
#             education=safe_get(user_data, "education", []),
#             experience=safe_get(user_data, "experience", []),
#             technical_skills=safe_get(user_data, "technical_skills", []),
#             languages=safe_get(user_data, "languages", []),
#             certifications=safe_get(user_data, "certifications", []),
#             projects=safe_get(user_data, "projects", []),
#             volunteering_experience=safe_get(user_data, "volunteering_experience", []),
#             awards=safe_get(user_data, "awards", [])
#         )
#         return HTMLResponse(content=html_content)

#     except Exception as e:
#         return error_response(code=500, error_message=f"Template rendering error: {str(e)}")

# @router.get("/api/download-cv/pdf/{header_id}/", tags=["CV Exporting"])
# async def download_cv_pdf(header_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

#     try:
#         user_id = int(user["user_id"])
#         user_data = await get_user_by_header_id(db, header_id)

#         if not user_data or user_data["user_id"] != user_id:
#             return error_response(code=403, error_message="You do not have permission to download this CV.")

#         template = env.get_template("resume_template.html")
#         html_content = template.render(**user_data)

#         pdf_buffer = pdfkit.from_string(html_content, False, options={
#             "page-size": "A4",
#             "margin-top": "10mm",
#             "margin-right": "10mm",
#             "margin-bottom": "10mm",
#             "margin-left": "10mm",
#             "encoding": "UTF-8",
#             "dpi": 300,
#             "enable-local-file-access": None
#         }, configuration=config)

#         return StreamingResponse(io.BytesIO(pdf_buffer), media_type="application/pdf",
#                                  headers={"Content-Disposition": f"attachment; filename={user_data.get('full_name', 'Generated_CV')}.pdf"})

#     except Exception as e:
#         return error_response(code=500, error_message=f"PDF generation error: {str(e)}")


# @router.get("/api/download-cv/docx/{header_id}/", tags=["CV Exporting"])
# async def download_cv_docx(header_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

#     try:
#         user_id = int(user["user_id"])
#         user_data = await get_user_by_header_id(db, header_id)

#         if not user_data or user_data["user_id"] != user_id:
#             return error_response(code=403, error_message="You do not have permission to download this CV.")

#         template = env.get_template("resume_template.html")
#         html_content = template.render(**user_data)

#         docx_buffer = await generate_docx_from_html(html_content)

#         return StreamingResponse(
#             docx_buffer,
#             media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#             headers={"Content-Disposition": f"attachment; filename={user_data.get('full_name', 'Generated_CV')}.docx"}
#         )

#     except Exception as e:
#         return error_response(code=500, error_message=f"Template rendering error: {str(e)}")
    

# @router.get("/api/regenerate-cv/{header_id}/", response_class=HTMLResponse, tags=["CV Exporting"])
# async def regenerate_cv(header_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
#     try:
#         user_id = int(user["user_id"])
#         user_data = await get_user_by_header_id(db, header_id)

#         if not user_data or user_data["user_id"] != user_id:
#             return error_response(code=403, error_message="You do not have permission to regenerate this CV.")

#         template = env.get_template("resume_template.html")
#         html_content = template.render(
#             full_name=safe_get(user_data, "full_name"),
#             job_title=safe_get(user_data, "job_title"),
#             email=safe_get(user_data, "email"),
#             phone_number=safe_get(user_data, "phone_number"),
#             address=safe_get(user_data, "address"),
#             years_of_experience=safe_get(user_data, "years_of_experience"),
#             github_profile=safe_get(user_data, "github_profile"),
#             linkedin_profile=safe_get(user_data, "linkedin_profile"),
#             objective=safe_get(user_data, "objective"),
#             education=safe_get(user_data, "education", []),
#             experience=safe_get(user_data, "experience", []),
#             technical_skills=safe_get(user_data, "technical_skills", []),
#             languages=safe_get(user_data, "languages", []),
#             certifications=safe_get(user_data, "certifications", []),
#             projects=safe_get(user_data, "projects", []),
#             volunteering_experience=safe_get(user_data, "volunteering_experience", []),
#             awards=safe_get(user_data, "awards", [])
#         )
#         return HTMLResponse(content=html_content)
    
#     except Exception as e:
#         return error_response(code=500, error_message=f"Template rendering error: {str(e)}")
    
# @router.post("/api/objectives/suggestions/", tags=["AI Enhancements"])
# async def generate_objective_suggestions(
#     request: ObjectiveSaveRequest, 
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")
        
#         if not header.job_title or not header.years_of_experience:
#             return error_response(code=400, error_message="Missing job title or years of experience in header.")

#         db_objective = Objective(
#             header_id=header.id,
#             description=request.description or "" 
#         )
#         db.add(db_objective)
#         await db.commit()
#         await db.refresh(db_objective)

#         ai_suggestions = await generate_objective_from_ai(
#             job_title=header.job_title,
#             years_of_experience=header.years_of_experience
#         )

#         return success_response(code=200, data={
#             "objective_id": db_objective.id,
#             "header_id": header.id,
#             "suggestions": ai_suggestions
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))



# @router.put("/api/objectives/save-description/{objective_id}/", tags=["AI Enhancements"])
# async def save_objective_description(
#     objective_id: int,
#     request: ObjectiveSaveRequest, 
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         objective = await db.get(Objective, objective_id)
#         if not objective:
#             return error_response(code=404, error_message="Objective not found.")

#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         if objective.header_id != header.id:
#             return error_response(code=403, error_message="Unauthorized access to this objective.")

#         objective.description = request.description
#         await db.commit()
#         await db.refresh(objective)

#         return success_response(code=200, data={
#             "objective_id": objective.id,
#             "description": request.description
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Error updating objective description", data=str(e))
    
# @router.post("/api/projects/generate-description/", tags=["AI Enhancements"])
# async def generate_project_description(
#     request: ProjectRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         existing_project_query = await db.execute(
#             select(Projects).where(
#                 Projects.header_id == header.id,
#                 Projects.project_name == request.project_name
#             )
#         )
#         existing_project = existing_project_query.scalars().first()

#         if existing_project:
#             project = existing_project
#         else:
#             project = Projects(
#                 header_id=header.id,
#                 project_name=request.project_name,
#                 description=""
#             )
#             db.add(project)
#             await db.commit()
#             await db.refresh(project)

#         # 4. جلب الاقتراحات من AI
#         ai_suggestions = await fetch_project_descriptions_from_ai(
#             project_name=request.project_name
#         )

#         return success_response(code=200, data={
#             "project_id": project.id,
#             "project_name": project.project_name,
#             "suggestions": ai_suggestions  
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


# @router.put("/api/projects/save-description/{project_id}/", tags=["AI Enhancements"])
# async def save_project_description(
#     project_id: int,
#     request: ProjectDescriptionSaveRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         project = await db.get(Projects, project_id)
#         if not project:
#             return error_response(code=404, error_message="Project not found.")

#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         if project.header_id != header.id or project.project_name != request.project_name:
#             return error_response(code=400, error_message="Header or project name mismatch.")

#         project.description = request.selected_description
#         await db.commit()
#         await db.refresh(project)

#         return success_response(code=200, data={
#             "project_id": project_id,
#             "description": request.selected_description
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Error updating project description", data=str(e))


# @router.post("/api/experiences/suggestions/", tags=["AI Enhancements"])
# async def generate_experience_suggestions(
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         result = await db.execute(
#             select(Experience).where(Experience.header_id == header.id)
#         )
#         experience = result.scalars().first()

#         if not experience:
#             return error_response(code=404, error_message="Experience not found for this user.")

#         ai_suggestions = await generate_experience_from_ai(
#             role=experience.role,
#             start_date=experience.start_date,
#             end_date=experience.end_date
#         )

#         return success_response(code=200, data={
#             "experience_id": experience.id,
#             "role": experience.role,
#             "suggestions": ai_suggestions
#         })

#     except Exception as e:
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


# @router.put("/api/experiences/save-description/{experience_id}/", tags=["AI Enhancements"])
# async def save_experience_description(
#     experience_id: int,
#     request: ExperienceSaveRequest,
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         experience = await db.get(Experience, experience_id)
#         if not experience:
#             return error_response(code=404, error_message="Experience not found.")

#         result = await db.execute(
#             select(Header).where(Header.user_id == int(user["user_id"]))
#         )
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         if experience.header_id != header.id:
#             return error_response(code=403, error_message="Unauthorized access to this experience.")

#         experience.description = request.selected_description
#         await db.commit()
#         await db.refresh(experience)

#         return success_response(code=200, data={
#             "experience_id": experience.id,
#             "description": request.selected_description
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Error updating experience description", data=str(e))

# @router.post("/api/skills/suggestions/", tags=["AI Enhancements"])
# async def generate_skills_suggestions(
#     request: GenerateSkillsRequest, 
#     user: dict = Depends(get_current_user),  
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
#         header = result.scalars().first()

#         if not header:
#             return error_response(code=404, error_message="Header not found for this user.")

#         db_skills_languages = SkillsLanguages(
#             header_id=header.id,
#             skills="",  
#             languages="",
#             level=None  
#         )
#         db.add(db_skills_languages)
#         await db.commit()
#         await db.refresh(db_skills_languages)

#         ai_suggestions = await generate_skills_from_ai(
#             job_title=header.job_title,
#             years_of_experience=header.years_of_experience
#         )

#         return success_response(code=200, data={
#             "skills_languages_id": db_skills_languages.id,
#             "suggestions": ai_suggestions
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Unexpected error occurred", data=str(e))

# @router.put("/api/skills/save/{skills_id}/", tags=["AI Enhancements"])
# async def save_skills(
#     skills_id: int, 
#     request: SaveSkillsRequest, 
#     user: dict = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         skills_record = await db.get(SkillsLanguages, skills_id)
#         if not skills_record:
#             return error_response(code=404, error_message="Skills record not found.")

#         header = await db.get(Header, skills_record.header_id)
#         if not header or header.user_id != int(user["user_id"]):
#             return error_response(code=403, error_message="Unauthorized access to this skills record.")

#         skills_record.skills = request.selected_skills
#         skills_record.languages = request.selected_language  
#         skills_record.level = request.selected_level  

#         await db.commit()
#         await db.refresh(skills_record) 

#         return success_response(code=200, data={
#             "skills": skills_record.skills,
#             "languages": skills_record.languages,
#             "level": skills_record.level
#         })

#     except Exception as e:
#         await db.rollback()
#         return error_response(code=500, error_message="Error updating skills", data=str(e))
