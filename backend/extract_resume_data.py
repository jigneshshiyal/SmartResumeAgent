from langgraph.graph import StateGraph, MessagesState
from langgraph.constants import START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
from resume_models import ResumeExtractionData
from prompt import RESUME_EXTRACTOR_PROMPT
from langchain_core.prompts import ChatPromptTemplate

    
from dotenv import load_dotenv
import os

# ---------------- Load env ----------------
load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash", api_key=GEMINI_API_KEY
)

extraction_model = gemini_model.with_structured_output(schema=ResumeExtractionData)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file.
        
    Returns:
        str: Extracted text from all pages.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Some pages may return None
        text += "\n"
    return text.strip()


prompt_template = ChatPromptTemplate.from_messages([
    (
        "system", RESUME_EXTRACTOR_PROMPT.strip()
    ),
    ("human", "Extract all possible information from the following resume text: {text}"),
])

def extract_data_from_resume(file_path: str) -> dict:
    resume_text = extract_text_from_pdf(file_path)
    prompt = prompt_template.invoke({"text": resume_text})
    response = extraction_model.invoke(prompt)
    return response.model_dump_json()


