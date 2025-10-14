from backend.core.base_service import TraceableService
from jinja2 import Environment, FileSystemLoader

class EmailTemplateService (TraceableService):
    def __init__(self, template_dir="/app/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_invitation(self, candidate_name, job_title, interview_date, interview_link, company_field):
        template = self.env.get_template("interview_invitation.html")
        return template.render(
            candidate_name=candidate_name,
            job_title=job_title,
            interview_date=interview_date,
            interview_link=interview_link,
            company_field=company_field
        )
