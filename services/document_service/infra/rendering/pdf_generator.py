from Domain.contracts.rendering.pdf_contract import PdfContract
from infra.rendering.playwright_renderer import render_pdf_from_html

class PdfGenerator(PdfContract):
  async  def render(self , html :str )-> bytes:
    return await render_pdf_from_html(html)
