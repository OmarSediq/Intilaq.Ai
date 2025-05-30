from pydantic import BaseModel

class JobData(BaseModel):
    job_title: str
    level: str = None
    description: str = None
