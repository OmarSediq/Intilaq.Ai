from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from app.utils.response_schemas import error_response

async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(code=exc.status_code, error_message=exc.detail)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(code=422, error_message="Validation Error", data=exc.errors())

async def global_exception_handler(request: Request, exc: Exception):
    return error_response(code=500, error_message="Internal Server Error", data=str(exc))
