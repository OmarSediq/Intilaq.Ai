from Domain.policies import retry_policy


class DocumentHandler:
    def __init__(self, routes: dict):
        self.routes = routes

    async def handle(self, envelope):

        route = self.routes.get(envelope.event_name)
        if not route:
            return

        mapper, use_case = route

        domain_event = mapper(envelope)

        await retry_policy.run(
            key=domain_event.idempotency_key,
            action=lambda: use_case.execute(domain_event)
        )
