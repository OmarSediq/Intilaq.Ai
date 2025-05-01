from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.database.models import Header, Projects
from app.schemas.cv import ProjectRequest, ProjectDescriptionSaveRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.services.ai_services import fetch_project_descriptions_from_ai

router = APIRouter()

@router.post("/api/projects/", tags=["Projects & Certifications"])
async def create_project(
    request: ProjectRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        project = Projects(**request.dict(exclude={"header_id"}), header_id=header.id)

        db.add(project)
        await db.commit()
        await db.refresh(project)

        return success_response(code=201, data={
            "message": "Project created successfully",
            "data": serialize_sqlalchemy_object(project)
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.get("/api/projects/{project_id}/", tags=["Projects & Certifications"])
async def get_project(
    project_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        project = await db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await db.get(Header, project.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to view this project.")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(project)})

    except Exception as e:
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.put("/api/projects/{project_id}/", tags=["Projects & Certifications"])
async def update_project(
    project_id: int,
    request: ProjectRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        project = await db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await db.get(Header, project.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to update this project.")

        for key, value in request.dict(exclude_unset=True).items():
            setattr(project, key, value)

        await db.commit()
        await db.refresh(project)

        return success_response(code=200, data={
            "message": "Project updated successfully",
            "data": serialize_sqlalchemy_object(project)
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.delete("/api/projects/{project_id}/", tags=["Projects & Certifications"])
async def delete_project(
    project_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        project = await db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found")

        header = await db.get(Header, project.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to delete this project.")

        await db.delete(project)
        await db.commit()

        return success_response(code=200, data={"message": "Project deleted successfully"})

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.post("/api/projects/generate-description/", tags=["AI Enhancements"])
async def generate_project_description(
    request: ProjectRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        existing_project_query = await db.execute(
            select(Projects).where(
                Projects.header_id == header.id,
                Projects.project_name == request.project_name
            )
        )
        existing_project = existing_project_query.scalars().first()

        if existing_project:
            project = existing_project
        else:
            project = Projects(
                header_id=header.id,
                project_name=request.project_name,
                description=""
            )
            db.add(project)
            await db.commit()
            await db.refresh(project)

        ai_suggestions = await fetch_project_descriptions_from_ai(project_name=request.project_name)

        return success_response(code=200, data={
            "project_id": project.id,
            "project_name": project.project_name,
            "suggestions": ai_suggestions
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.put("/api/projects/save-description/{project_id}/", tags=["AI Enhancements"])
async def save_project_description(
    project_id: int,
    request: ProjectDescriptionSaveRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        project = await db.get(Projects, project_id)
        if not project:
            return error_response(code=404, error_message="Project not found.")

        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        if project.header_id != header.id or project.project_name != request.project_name:
            return error_response(code=400, error_message="Header or project name mismatch.")

        project.description = request.selected_description
        await db.commit()
        await db.refresh(project)

        return success_response(code=200, data={
            "project_id": project_id,
            "description": request.selected_description
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Error updating project description", data=str(e))
