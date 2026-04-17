from Domain.contracts.rendering.docx_contract import DocxContract
import os
import asyncio


class DocxRenderer(DocxContract):
    async def render(self, html: str) -> bytes:

        process = await asyncio.create_subprocess_exec(
            "pandoc",
            "-f", "html",
            "-t", "docx",
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate(
            input=html.encode("utf-8")
        )

        if process.returncode != 0:
            raise RuntimeError(f"Pandoc failed: {stderr.decode()}")

        return stdout
    

    
 