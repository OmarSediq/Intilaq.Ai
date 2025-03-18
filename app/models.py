from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON,Date,func
from sqlalchemy.orm import declarative_base, relationship
from passlib.context import CryptContext
from datetime import datetime, timezone,date



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base = declarative_base()

# Existing User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)  
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Integer, default=0)  
    # sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


    def verify_password(self, plain_password: str) -> bool:
        """ 
        Verify if the plain password matches the hashed password.
        """
        return pwd_context.verify(plain_password, self.hashed_password)

    def set_password(self, plain_password: str):
        """
        Hash and set the password for the user.
        """
        self.hashed_password = pwd_context.hash(plain_password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, is_verified={self.is_verified})>"
    
    headers = relationship("Header", back_populates="user", cascade="all, delete-orphan")



    # # Session Model 
    # class Session(Base):
    #     __tablename__ = "sessions"
        
    #     session_id = Column(Integer, primary_key=True, index=True)
    #     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE")) 
    #     status = Column(String(50), default="active")  

    #     user = relationship("User", back_populates="sessions")

    #     def __repr__(self):
    #         return f"<Session(session_id={self.session_id}, user_id={self.user_id}, status={self.status})>"




# Existing ResetCode Model
class ResetCode(Base):
    __tablename__ = "reset_codes"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    code = Column(String(6), nullable=False)
    # created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 

    def __repr__(self):
        return f"<ResetCode(id={self.id}, email={self.email}, code={self.code}, created_at={self.created_at})>"


# Header Table (Main User Table)
class Header(Base):
    __tablename__ = 'header'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    job_title = Column(String(255))
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20))
    address = Column(Text)
    years_of_experience = Column(Integer)
    github_profile = Column(String(255))
    linkedin_profile = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 

    # Relationships
    user = relationship("User", back_populates="headers")
    education = relationship("Education", back_populates="header", cascade="all, delete")
    skills_languages = relationship("SkillsLanguages", back_populates="header", cascade="all, delete")
    certifications = relationship("Certifications", back_populates="header", cascade="all, delete-orphan")
    projects = relationship("Projects", back_populates="header", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="header", cascade="all, delete-orphan")
    volunteering_experience = relationship("VolunteeringExperience", back_populates="header", cascade="all, delete-orphan")
    awards = relationship("Awards", back_populates="header", cascade="all, delete-orphan")
    objective = relationship("Objective", back_populates="header", cascade="all, delete-orphan")

# Education Table (Mandatory)
class Education(Base):
    __tablename__ = 'education'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)
    degree_and_major = Column(String(255), nullable=False)
    school = Column(String(255), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    description = Column(Text)

    header = relationship("Header", back_populates="education")

# Skills & Languages Table (Mandatory)
class SkillsLanguages(Base):
    __tablename__ = 'skills_languages'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)
    skills = Column(Text, nullable=True)
    languages = Column(Text, nullable=False)
    level = Column(String(50))

    header = relationship("Header", back_populates="skills_languages")

# Certifications Table (Optional)
class Certifications(Base):
    __tablename__ = 'certifications'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)
    certification_title = Column(String(255))
    upload = Column(Text,nullable=True)
    link = Column(Text, nullable=True)  

    header = relationship("Header", back_populates="certifications")

# Projects Table (Optional)
class Projects(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)
    project_name = Column(String(255))
    description = Column(Text,nullable=True)
    link = Column(Text,nullable=True)

    header = relationship("Header", back_populates="projects")

# Experience Table (Optional)
class Experience(Base):
    __tablename__ = 'experience'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)  
    role = Column(String(255))
    company_name = Column(String(255))
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)

    header = relationship("Header", back_populates="experience")


# Volunteering Experience Table (Optional)
class VolunteeringExperience(Base):
    __tablename__ = 'volunteering_experience'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)
    organization = Column(String(255))
    role = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    description = Column(Text,nullable=True)

    header = relationship("Header", back_populates="volunteering_experience")

# Awards Table (Optional)
class Awards(Base):
    __tablename__ = 'awards'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)
    award = Column(String(255))
    organization = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)

    header = relationship("Header", back_populates="awards")

# Objective Table (Optional)
class Objective(Base):
    __tablename__ = 'objective'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    header_id = Column(Integer, ForeignKey('header.id'), nullable=False)
    description = Column(Text, nullable=True)   

    header = relationship("Header", back_populates="objective")


    

    