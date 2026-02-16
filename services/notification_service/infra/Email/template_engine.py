from jinja2 import Environment, FileSystemLoader, select_autoescape

template_env = Environment(
    loader=FileSystemLoader("/app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)
