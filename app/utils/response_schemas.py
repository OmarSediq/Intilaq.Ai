from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional
from datetime import date
class BaseResponseModel(BaseModel):  
    status: str
    error: Optional[str] = None
    code: int
    data: Optional[Any] = None 



def serialize_sqlalchemy_object(obj):
    if hasattr(obj, "__table__"):
        return {
            column.name: str(getattr(obj, column.name)) if isinstance(getattr(obj, column.name), date) 
            else getattr(obj, column.name) 
            for column in obj.__table__.columns
        }
    elif isinstance(obj, list):
        return [serialize_sqlalchemy_object(item) for item in obj]
    return obj  

def success_response(code: int = 200, data: Any = None, message: str = "Success"):
    response_data = BaseResponseModel(
        status="success",
        error=None,
        code=code,
        data=serialize_sqlalchemy_object(data) if data is not None else {"message": message}
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

# credentials: "include"
