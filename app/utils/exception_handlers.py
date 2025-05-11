from fastapi import Request, HTTPException,status
from fastapi.exceptions import RequestValidationError
from app.utils.response_schemas import error_response
import logging
logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE:
        return error_response(
            code=415,
            error_message="Unsupported Media Type. Please use application/json content-type."
        )

    return error_response(code=exc.status_code, error_message=exc.detail)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(code=422, error_message=str(exc))

async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return error_response(code=500, error_message="Internal Server Error")

def register_exception_handlers(app):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


