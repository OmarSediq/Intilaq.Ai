from Domain.contracts.pdf_renderer import PdfRenderer
from infra.rendering.pdf.playwright_renderer import render_pdf_from_html

class PdfGenerator(PdfRenderer):
  async  def generate(self , html :str )-> bytes:
    return await render_pdf_from_html(html)
