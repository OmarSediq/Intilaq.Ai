from dependency_injector import containers , providers

from backend.core.containers.dispatchers_container import DispatchersContainer
from backend.core.containers.services_container import ServicesContainer
from .ai_container import AIContainer
from .infra_container import InfraContainer
from .repositories_container import RepositoriesContainer 


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    infra = providers.Container(InfraContainer , config=config)
    repos = providers.Container(RepositoriesContainer )
    ai = providers.Container(AIContainer , config=config)
    service = providers.Container(ServicesContainer , infra = infra)
    dispatcher = providers.Container(DispatchersContainer )

