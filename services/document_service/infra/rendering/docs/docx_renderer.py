from docxtpl import DocxTemplate
from io import BytesIO
from Domain.contracts.docx_renderer import DocxRenderer

class DocxRenderer(DocxRenderer):
    def __init__(self, template_path: str):
        self.template_path = template_path

    async def generate(self, snapshot: dict) -> bytes:

        doc = DocxTemplate(self.template_path)

        # render = snapshot مباشرة
        doc.render(snapshot)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return buffer.read()
