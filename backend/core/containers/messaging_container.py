from dependency_injector import containers, providers
from backend.data_access.redis.event_publishers.email_event_publisher import RedisEmailEventPublisher

class MessagingContainer(containers.DeclarativeContainer):
    infra = providers.DependenciesContainer()

    email_event_publisher = providers.Factory(
        RedisEmailEventPublisher,
        redis=infra.redis_client,
    )
