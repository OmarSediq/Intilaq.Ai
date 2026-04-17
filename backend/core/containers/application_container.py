from dependency_injector import containers , providers
from backend.core.containers.services_container import ServicesContainer
from backend.core.containers.messaging_container import MessagingContainer
from .ai_container import AIContainer
from .infra_container import InfraContainer
from .repositories_container import RepositoriesContainer 


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    infra = providers.Container(InfraContainer , config=config)
    repos = providers.Container(RepositoriesContainer  ,  infra=infra )
    ai = providers.Container(AIContainer , config=config)
    service = providers.Container(ServicesContainer , infra = infra , repos = repos )
    messaging = providers.Container(MessagingContainer,infra=infra)
    
 

    # # ========= Re-export Infra =========
    # mongo_hr_db = infra.mongo_hr_db
    # mongo_interview_db = infra.mongo_interview_db
    # mongo_resumes_db = infra.mongo_resumes_db

    # hr_video_bucket = infra.hr_video_bucket
    # resumes_bucket = infra.resumes_bucket

    # redis_client = infra.redis_client
