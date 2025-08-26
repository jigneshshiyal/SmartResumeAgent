from pydantic import BaseModel, Field
from typing import List, Optional

class EducationEntry(BaseModel):
    degree: Optional[str] = ""
    institution: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    grade: Optional[str] = ""


class ProjectEntry(BaseModel):
    project_name: Optional[str] = ""
    description: Optional[str] = ""
    technologies: List[str] = Field(default_factory=list)
    link: Optional[str] = ""


class ExperienceEntry(BaseModel):
    job_title: Optional[str] = ""
    company: Optional[str] = ""
    location: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    responsibilities: List[str] = Field(default_factory=list)


class Links(BaseModel):
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""


class OtherInfo(BaseModel):
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    links: Links = Field(default_factory=Links)


class ResumeExtractionData(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    education: List[EducationEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    other_info: OtherInfo = Field(default_factory=OtherInfo)