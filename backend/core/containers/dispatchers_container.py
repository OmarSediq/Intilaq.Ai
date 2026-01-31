from dependency_injector import containers , providers
from backend.core.job_dispatchers.redis_stream_dispatcher import RedisStreamDispatcher

class DispatchersContainer(containers.DeclarativeContainer):
    infra = providers.DependenciesContainer()

    # video_dispatcher = providers.Singleton(RedisStreamDispatcher , redis_client = infra.redis_client , stream_name = "video_jobs")
    # text_dispatcher = providers.Singleton(
    #     RedisStreamDispatcher,
    #     redis_client=infra.redis_client,
    #     stream_name="text_jobs"
    # )
    # email_dispatcher = providers.Singleton(
    #     RedisStreamDispatcher,
    #     redis_client=infra.redis_client,
    #     stream_name="email_jobs"
    # )

    # docs_dispatcher = providers.Singleton(
    #     RedisStreamDispatcher,
    #     redis_client=infra.redis_client,
    #     stream_name="docs_jobs"
    # )

   

    