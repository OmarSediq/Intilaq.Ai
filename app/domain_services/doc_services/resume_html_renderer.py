from jinja2 import Environment

class ResumeHTMLRenderer:
    def __init__(self, env: Environment):
        self.env = env

    def render(self, user_data: dict) -> str:
        template = self.env.get_template("resume_template.html")
        return template.render(**{
            k: v if not isinstance(v, str) else v or ""
            for k, v in user_data.items()
        })
