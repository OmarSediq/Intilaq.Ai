from docxtpl import DocxTemplate
from io import BytesIO
from Domain.contracts.rendering.docx_contract import DocxContract

class DocxRenderer(DocxContract):
    def __init__(self, template_path: str):
        self.template_path = template_path

    async def render(self, snapshot: dict) -> bytes:

        doc = DocxTemplate(self.template_path)

        doc.render(snapshot)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return buffer.read()
