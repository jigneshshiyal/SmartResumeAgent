from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from resume_models import ResumeExtractionData

# ---------------- Load env ----------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash", api_key=GEMINI_API_KEY
)

customize_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a resume customization assistant.
        Update ONLY the "skills" field in the resume JSON using the provided job description.
        Keep all other fields unchanged.
        Return valid JSON only."""
    ),
    ("human", "Resume JSON:\n{resume_json}\n\nJob Post:\n{job_post}")
])

def change_resume_json(resume_json: str, job_post: str) -> dict:
    prompt = customize_prompt_template.invoke({
        "resume_json": resume_json,
        "job_post": job_post
    })
    response = gemini_model.with_structured_output(schema=ResumeExtractionData).invoke(prompt)
    return response.model_dump_json()