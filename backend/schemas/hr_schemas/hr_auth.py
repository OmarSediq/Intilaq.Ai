from pydantic import BaseModel, EmailStr

class HrSignupRequest(BaseModel):
    name: str
    company_name: str
    business_email: EmailStr
    company_field: str
    password: str
    confirm_password: str

class HrLoginRequest(BaseModel):
    business_email: EmailStr
    password: str

class HrVerifyRequest(BaseModel):
    code: str

class HrResendCodeRequest(BaseModel):
    business_email: EmailStr



  