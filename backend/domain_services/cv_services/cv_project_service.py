from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.data_access.postgres.cv.project_repository import ProjectRepository
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

        return success_response(code=201, data={
        "message": "Project created successfully",
        "project": project
    })

    async def get(self, project_id: int, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.header_repo.get_by_id(project.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        return success_response(code=200, data={"project": project})


    async def update(self, project_id: int, request, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.header_repo.get_by_id(project.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        updated_project = await self.project_repo.update(project, request.dict(exclude_unset=True))

        return success_response(code=200, data={
        "message": "Project updated successfully",
        "project": updated_project
    })


    async def delete(self, project_id: int, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.header_repo.get_by_id(project.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        await self.project_repo.delete(project)
        return success_response(code=200, data={"message": "Project deleted successfully"})


    async def generate_description(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        existing = await self.project_repo.get_by_name_and_header(header.id, request.project_name)
        if existing:
            project = existing
        else:
            project = await self.project_repo.create({
                "header_id": header.id,
                "project_name": request.project_name,
                "description": ""
            })

        suggestions = await self.gemini_service.fetch_project_descriptions(request.project_name)

        return success_response(code=200, data={
        "project_id": project.id,
        "project_name": project.project_name,
        "suggestions": suggestions
    })


    async def save_description(self, project_id: int, request, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        if project.header_id != header.id or project.project_name != request.project_name:
            return error_response(code=400, error_message="Header or project name mismatch")

        updated = await self.project_repo.update(project, {"description": request.selected_description})

        return success_response(code=200, data={
        "message": "Project description updated",
        "project": updated
    })
