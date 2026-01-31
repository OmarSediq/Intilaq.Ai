from sympy import im
from backend.domain_services.doc_services.docx_generator_services import DocxGenerator
from backend.domain_services.doc_services.pdf_generator_service import PDFGeneratorService
from backend.domain_services.doc_services.resume_html_renderer import ResumeHTMLRenderer
from backend.core.config import env  
from backend.core.containers.repositories_container import RepositoriesContainer
from dependency_injector.wiring import inject , Provide

# def get_docx_generator() -> DocxGenerator:
#     return DocxGenerator()

# def get_pdf_generator() -> PDFGeneratorService:
#     return PDFGeneratorService()
# @inject 
# def get_resume_html_renderer ()



def get_resume_html_renderer() -> ResumeHTMLRenderer:
    return ResumeHTMLRenderer(env)


