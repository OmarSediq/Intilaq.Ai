from Core.base_service import TraceableService
from Core.logger import logger


class DocumentHandler(TraceableService):
    def __init__(self, routes: dict , retry_policy):
        self.routes = routes
        self.retry_policy = retry_policy
    async def handle(self, envelope):

        route = self.routes.get(envelope.event_name)


        if not route:
            logger.warning(
                "event.routing.not_found",
                extra={
                    "event_name": envelope.event_name,
                    "available_routes": list(self.routes.keys()),
                    "service": "document_service"
                }
            )
            return

        mapper, use_case = route

        domain_event = mapper(envelope)

        await self.retry_policy.run(
            key=domain_event.idempotency_key,
            action=lambda: use_case.execute(domain_event)
        )
