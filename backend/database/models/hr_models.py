from sqlalchemy import Column, Integer, String, DateTime,func
from passlib.context import CryptContext
from backend.database.models.base import Base



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class HrUser(Base):
    __tablename__ = 'hr_users'
    __table_args__ = {'schema': 'hr'}
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    business_email = Column(String(255), unique=True, nullable=False)
    company_field = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Integer, default=0)

    def set_password(self, plain_password: str):
        self.hashed_password = pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)
    

class ResetCode(Base):
    __tablename__ = "hr_reset_codes"
    __table_args__ = {'schema': 'hr'}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)  
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ResetCode(id={self.id}, email={self.email}, code={self.code}, created_at={self.created_at})>"
