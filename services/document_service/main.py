# main.py
from fastapi import FastAPI, Response, HTTPException
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError
import asyncio

app = FastAPI(title="PDF Test Service (Playwright)")

@app.get("/health")
async def health():
    return {"status": "ok"}

async def render_html_to_pdf_bytes(html: str, timeout: int = 30) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        pdf_bytes = await page.pdf(format="A4")
        await browser.close()
        return pdf_bytes

@app.post("/render")
async def render_pdf():
    html = "<meta charset='utf-8'><h1>Hello PDF</h1><p>هذه تجربة</p>"
    try:
        pdf_bytes = await asyncio.wait_for(render_html_to_pdf_bytes(html), timeout=30)
        return Response(content=pdf_bytes, media_type="application/pdf")
    except PWTimeoutError as e:
        raise HTTPException(status_code=504, detail="Rendering timed out: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
