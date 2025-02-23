from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional

class BaseResponseModel(BaseModel):
    status: str
    error: Optional[str] = None
    code: int
    data: Optional[Any] = None

def success_response(code: int = 200, data: Any = None, message: str = "Success"):
    response_data = BaseResponseModel(
        status="success",
        error=None,
        code=code,
        data=data if data is not None else {"message": message}
    )
    return JSONResponse(content=response_data.dict(), status_code=code)

def error_response(code: int = 400, error_message: str = "An error occurred", data: Any = None):
    response_data = BaseResponseModel(
        status="error",
        error=error_message,
        code=code,
        data=data
    )
    return JSONResponse(content=response_data.dict(), status_code=code)
