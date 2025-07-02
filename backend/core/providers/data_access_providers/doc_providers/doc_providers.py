from backend.domain_services.doc_services.docx_generator_services import DocxGenerator
from backend.domain_services.doc_services.pdf_generator_service import PDFGeneratorService
from backend.domain_services.doc_services.resume_html_renderer import ResumeHTMLRenderer
from backend.core.config import env  

def get_docx_generator() -> DocxGenerator:
    return DocxGenerator()

def get_pdf_generator() -> PDFGeneratorService:
    return PDFGeneratorService()

def get_resume_html_renderer() -> ResumeHTMLRenderer:
    return ResumeHTMLRenderer(env)
