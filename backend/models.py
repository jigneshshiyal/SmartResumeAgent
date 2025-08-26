from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    resumes = relationship("Resume", back_populates="owner")
    customizations = relationship("ResumeCustomization", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    extracted_data = Column(JSON)  # store parsed resume content
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="resumes")
    customizations = relationship("ResumeCustomization", back_populates="resume")

class ResumeCustomization(Base):
    __tablename__ = "resume_customizations"

    id = Column(Integer, primary_key=True, index=True)
    job_post_text = Column(Text, nullable=False)
    customized_data = Column(JSON, nullable=False)

    # Foreign Keys
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    resume = relationship("Resume", back_populates="customizations")
    user = relationship("User", back_populates="customizations")