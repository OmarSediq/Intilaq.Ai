from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_models import Projects

class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Projects:
        project = Projects(**data)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: int) -> Projects | None:
        return await self.db.get(Projects, project_id)

    async def get_by_name_and_header(self, header_id: int, project_name: str) -> Projects | None:
        result = await self.db.execute(
            select(Projects).where(
                Projects.header_id == header_id,
                Projects.project_name == project_name
            )
        )
        return result.scalars().first()

    async def update(self, project: Projects, data: dict) -> Projects:
        for key, value in data.items():
            setattr(project, key, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Projects):
        await self.db.delete(project)
        await self.db.commit()
