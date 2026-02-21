# infrastructure/email/templates.py
from infra.Email.template_engine import template_env

def render_email_template(template_name: str, context: dict) -> str:
    template = template_env.get_template(f"{template_name}.html")
    return template.render(**context)



