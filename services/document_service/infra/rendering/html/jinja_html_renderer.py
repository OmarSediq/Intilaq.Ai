from jinja2 import Environment , FileSystemLoader
from Domain.contracts.html_renderer import HtmlRenderer


class JinjaHtmlRenderer(HtmlRenderer):
    def __init__(self , template_dir:str):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
        )
        self.template = self.env.get_template("resume_template.html")

    def render (self , snapshot:dict)-> str : 
        return self.template.render(**snapshot)
    

    