import pdfkit

class PDFGeneratorService:
    def __init__(self, wkhtmltopdf_path="/usr/bin/wkhtmltopdf"):
        self.config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    def generate(self, html_content: str) -> bytes:
        return pdfkit.from_string(html_content, False, options={
            "page-size": "A4",
            "margin-top": "10mm",
            "margin-right": "10mm",
            "margin-bottom": "10mm",
            "margin-left": "10mm",
            "encoding": "UTF-8",
            "dpi": 300,
            "enable-local-file-access": None
        }, configuration=self.config)
