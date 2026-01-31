from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.skill_language_repository import SkillsLanguagesRepository

# def get_skills_languages_repository(
#     db: AsyncSession = Depends(get_db)
# ) -> SkillsLanguagesRepository:
#     return SkillsLanguagesRepository(db)

@inject 
def get_skills_languages_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.skill_language_repository_factory]
)-> SkillsLanguagesRepository: 
    return factory(db)