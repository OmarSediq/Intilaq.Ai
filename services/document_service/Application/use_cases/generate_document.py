from Domain.contracts.mongo.snapshot_contract import CvSnapshotRepository
from Domain.contracts.rendering.html_contract import HtmlContract
from Domain.contracts.mongo.document_contract import DocumentContract
from Domain.contracts.rendering.pdf_contract import PdfContract
from Domain.contracts.rendering.docx_contract import DocxContract
from Domain.contracts.events.document_events import DocumentGenerationRequested
from Application.mappers.snapshot_to_template_mapper import SnapshotToTemplateMapper
class GenerateDocumentUseCase:

    def __init__(
        self,
        snapshot_repo: CvSnapshotRepository,
        html_contract: HtmlContract,
        pdf_contract: PdfContract,
        docx_contract: DocxContract,
        document_repo: DocumentContract,
    ):
        self._snapshot_repo = snapshot_repo
        self._html_contract = html_contract
        self._pdf_contract = pdf_contract
        self._docx_contract = docx_contract
        self._document_repo = document_repo
     
    async def execute(self, event : DocumentGenerationRequested)-> None:
        

        snapshot = await self._snapshot_repo.get_by_id(event.snapshot_id)
        context = SnapshotToTemplateMapper.map(snapshot["data"])

        html = self._html_contract.render(context)
        html_id=await self._document_repo.save(
            snapshot_id=event.snapshot_id,
            document_type="html",
            content=html.encode("utf-8"),
        )

        pdf_bytes = await self._pdf_contract.render(html)
        pdf_id = await self._document_repo.save(
            snapshot_id=event.snapshot_id,
            document_type="pdf",
            content=pdf_bytes,
        )


        docx_bytes = await self._docx_contract.render(html)
        docx_id = await self._document_repo.save(
            snapshot_id=event.snapshot_id,
            document_type="docx",
            content=docx_bytes,
        )

        await self._snapshot_repo.attach_documents(
            event.snapshot_id,
            {
                "pdf": pdf_id,
                "html": html_id,
                "docx": docx_id,
            },
        )




