# application/handlers/notification_handler.py

from Application.Mappers.invitation_event_mapper import map_envelope_to_invitation_event

class NotificationHandler:

    def __init__(self, invitation_use_case):
        self.invitation_use_case = invitation_use_case

    async def handle(self, envelope):

        if envelope.event_name != "notification.email.interview_invitation":
            return

        domain_event = map_envelope_to_invitation_event(envelope)

        await self.invitation_use_case.execute(domain_event)
