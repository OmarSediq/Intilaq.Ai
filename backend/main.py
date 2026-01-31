from fastapi.openapi.docs import get_swagger_ui_html
from backend.core.bootstrap.app_factory import create_app

app = create_app()

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="IntilaqAI - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css",
        init_oauth={},
        swagger_favicon_url="",
    ).update({
        "swaggerOptions": {
            "persistAuthorization": True,
            "withCredentials": True
        }
    })