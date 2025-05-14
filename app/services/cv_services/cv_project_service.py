from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_section_models import Header, Projects
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.services.ai_services import fetch_project_descriptions_from_ai

class CVProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_header(self, user_id: int):
        result = await self.db.execute(select(Header).where(Header.user_id == user_id))
        return result.scalars().first()

    async def create(self, request, user_id: int):
        header = await self._get_user_header(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        project = Projects(**request.dict(exclude={"header_id"}), header_id=header.id)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)

        return success_response(code=201, data={
            "message": "Project created successfully",
            "data": serialize_sqlalchemy_object(project)
        })

    async def get(self, project_id: int, user_id: int):
        project = await self.db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.db.get(Header, project.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(project)})

    async def update(self, project_id: int, request, user_id: int):
        project = await self.db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.db.get(Header, project.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        for key, value in request.dict(exclude_unset=True).items():
            setattr(project, key, value)

        await self.db.commit()
        await self.db.refresh(project)

        return success_response(code=200, data={
            "message": "Project updated successfully",
            "data": serialize_sqlalchemy_object(project)
        })

    async def delete(self, project_id: int, user_id: int):
        project = await self.db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self.db.get(Header, project.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        await self.db.delete(project)
        await self.db.commit()

        return success_response(code=200, data={"message": "Project deleted successfully"})

    async def generate_description(self, request, user_id: int):
        header = await self._get_user_header(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        query = await self.db.execute(
            select(Projects).where(
                Projects.header_id == header.id,
                Projects.project_name == request.project_name
            )
        )
        existing_project = query.scalars().first()

        if existing_project:
            project = existing_project
        else:
            project = Projects(header_id=header.id, project_name=request.project_name, description="")
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)

        ai_suggestions = await fetch_project_descriptions_from_ai(request.project_name)

        return success_response(code=200, data={
            "project_id": project.id,
            "project_name": project.project_name,
            "suggestions": ai_suggestions
        })

    async def save_description(self, project_id: int, request, user_id: int):
        project = await self.db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await self._get_user_header(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        if project.header_id != header.id or project.project_name != request.project_name:
            return error_response(code=400, error_message="Header or project name mismatch")

        project.description = request.selected_description
        await self.db.commit()
        await self.db.refresh(project)

        return success_response(code=200, data={
            "project_id": project_id,
            "description": request.selected_description
        })
