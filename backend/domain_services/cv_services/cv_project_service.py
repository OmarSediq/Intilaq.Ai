from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.data_access.postgres.cv.project_repository import ProjectRepository
from backend.schemas.cv_schema import ProjectResponse , ProjectDescriptionSaveRequest
from backend.utils.response_schemas import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService 

class CVProjectService:
    def __init__(self, db: AsyncSession, project_repo: ProjectRepository, header_repo: CVHeaderRepository , gemini_service : GeminiAIService):
        self.db = db
        self.project_repo = project_repo
        self.header_repo = header_repo
        self.gemini_service = gemini_service

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        project = await self.project_repo.create({
            **request.dict(exclude={"header_id"}),
            "header_id": header.id
        })
        project_data = ProjectResponse.model_validate(project)
        return success_response(code=201, data={
        "message": "Project created successfully",
        "project":  project_data.model_dump()
    })


    async def generate_description(self, project_id: int, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        project = await self.project_repo.get_by_id(project_id)
        if not project or project.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this project")

        suggestions = await self.gemini_service.fetch_project_descriptions(project.project_name)

        return success_response(code=200, data={
            "project_id": project.id,
            "project_name": project.project_name,
            "suggestions": suggestions
        })

    async def save_description(self, project_id: int, request: ProjectDescriptionSaveRequest, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        if project.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this project")

        updated = await self.project_repo.update(project, {"description": request.selected_description})

        return success_response(code=200, data={
            "message": "Project description updated",
            "project": ProjectResponse.model_validate(updated).model_dump()
        })
