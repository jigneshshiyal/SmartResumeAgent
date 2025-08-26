from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    resumes = relationship("Resume", back_populates="owner")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    extracted_data = Column(JSON)  # store parsed resume content
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="resumes")