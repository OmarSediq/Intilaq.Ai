from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

async def render_pdf_from_html(html: str) -> bytes:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
            )
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")

            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm",
                },
            )

            await browser.close()
            return pdf_bytes

    except PWTimeoutError:
        raise RuntimeError("PDF rendering timeout")
