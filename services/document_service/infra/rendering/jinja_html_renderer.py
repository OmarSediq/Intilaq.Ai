from jinja2 import Environment , FileSystemLoader
from Domain.contracts.rendering.html_contract import HtmlContract
from utils.date_utils import date_format

class JinjaHtmlRenderer(HtmlContract):
    def __init__(self , template_dir:str):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
        )
        self.env.filters["date_format"] = date_format   
        self.template = self.env.get_template("resume_template.html")
        
    def render (self , snapshot:dict)-> str : 
        return self.template.render(**snapshot)
    

    