class NotificationHandler:

    def __init__(self, routes: dict):
        self.routes = routes

    async def handle(self, envelope):

        route = self.routes.get(envelope.event_name)
        if not route:
            return

        mapper, use_case = route

        domain_event = mapper(envelope)

        await use_case.execute(domain_event)
