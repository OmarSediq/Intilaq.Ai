from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Header, Projects
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.services.ai_services import fetch_project_descriptions_from_ai


async def create_project_service(request, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    result = await db.execute(select(Header).where(Header.user_id == user_id))
    header = result.scalars().first()
    if not header:
        return error_response(code=404, error_message="Header not found")

    project = Projects(**request.dict(exclude={"header_id"}), header_id=header.id)
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return success_response(code=201, data={
        "message": "Project created successfully",
        "data": serialize_sqlalchemy_object(project)
    })


async def get_project_service(project_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    project = await db.get(Projects, project_id)
    if not project:
        return error_response(code=404, error_message="Project not found")

    header = await db.get(Header, project.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized")

    return success_response(code=200, data={"data": serialize_sqlalchemy_object(project)})


async def update_project_service(project_id: int, request, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    project = await db.get(Projects, project_id)
    if not project:
        return error_response(code=404, error_message="Project not found")

    header = await db.get(Header, project.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)

    return success_response(code=200, data={
        "message": "Project updated successfully",
        "data": serialize_sqlalchemy_object(project)
    })


async def delete_project_service(project_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    project = await db.get(Projects, project_id)
    if not project:
        return error_response(code=404, error_message="Project not found")

    header = await db.get(Header, project.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized")

    await db.delete(project)
    await db.commit()

    return success_response(code=200, data={"message": "Project deleted successfully"})


async def generate_project_description_service(request, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    result = await db.execute(select(Header).where(Header.user_id == user_id))
    header = result.scalars().first()
    if not header:
        return error_response(code=404, error_message="Header not found")

    existing_query = await db.execute(
        select(Projects).where(
            Projects.header_id == header.id,
            Projects.project_name == request.project_name
        )
    )
    existing_project = existing_query.scalars().first()

    if existing_project:
        project = existing_project
    else:
        project = Projects(header_id=header.id, project_name=request.project_name, description="")
        db.add(project)
        await db.commit()
        await db.refresh(project)

    ai_suggestions = await fetch_project_descriptions_from_ai(request.project_name)

    return success_response(code=200, data={
        "project_id": project.id,
        "project_name": project.project_name,
        "suggestions": ai_suggestions
    })


async def save_project_description_service(project_id: int, request, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    project = await db.get(Projects, project_id)
    if not project:
        return error_response(code=404, error_message="Project not found")

    result = await db.execute(select(Header).where(Header.user_id == user_id))
    header = result.scalars().first()
    if not header:
        return error_response(code=404, error_message="Header not found")

    if project.header_id != header.id or project.project_name != request.project_name:
        return error_response(code=400, error_message="Header or project name mismatch")

    project.description = request.selected_description
    await db.commit()
    await db.refresh(project)

    return success_response(code=200, data={
        "project_id": project_id,
        "description": request.selected_description
    })
