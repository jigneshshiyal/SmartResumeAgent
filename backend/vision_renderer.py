import base64
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from weasyprint import HTML
import tempfile
import os
from dotenv import load_dotenv
from models import User, Resume, ResumeCustomization
from langchain_core.messages import SystemMessage

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Base chat model (multimodal)
vision_model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    api_key=GEMINI_API_KEY,
    # you can tune generation params here if you like
)

SYSTEM_PROMPT = """You are a resume layout generator.
You will be given:
1) A screenshot/photo of a resume's layout.
2) A JSON object containing resume data.

Your job:
- Produce a single complete HTML document (<!DOCTYPE html> ... </html>) for an A4-sized resume that *visually* follows the look & structure inspired by the image.
- Use INLINE CSS only (no external CSS, no JS, no external fonts).
- Fill the content strictly from the provided JSON data (do not hallucinate). If a field is missing, skip it gracefully.
- Optimize for print (A4): small margins (e.g., 1.5cm), consistent typography, clear hierarchy, balanced use of whitespace.
- Mobile/desktop preview is not required; target print quality.
- Return HTML only. No explanations.
"""

HTML_PROMPT_TMPL = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human",
     "Use the following resume JSON to populate the template:\n\n{resume_json}\n\n"
     "Now generate the full inline-CSS HTML for an A4 resume that matches the look of the attached image.")
])

from weasyprint import HTML, CSS


def html_to_pdf_bytes(html: str):
    css = CSS(string="""
        @page {
            size: A4;
            margin: 1.5cm;
        }
        body {
            margin: 0 auto;
            box-sizing: border-box;
        }
        * {
            max-width: 100%;
            box-sizing: border-box;
        }
    """)
    pdf_bytes = HTML(string=html).write_pdf(stylesheets=[css])
    return pdf_bytes


def _encode_image_to_data_uri(image_bytes: bytes, filename: str) -> str:
    import mimetypes
    mime, _ = mimetypes.guess_type(filename)
    mime = mime or "image/png"
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def _get_resume_json_for_user(
    db: Session,
    user: User,
    source: str,
    customization_id: Optional[int]
) -> Tuple[str, Optional[int]]:
    """
    Returns (resume_json_string, customization_id_used)
    """
    if source == "customized":
        q = db.query(ResumeCustomization).filter(ResumeCustomization.user_id == user.id)
        if customization_id:
            q = q.filter(ResumeCustomization.id == customization_id)
        customization = q.order_by(ResumeCustomization.id.desc()).first()
        if not customization:
            raise ValueError("No customized resume found for this user.")
        return customization.customized_data, customization.id
    else:
        # original (latest extracted resume)
        resume = (
            db.query(Resume)
            .filter(Resume.user_id == user.id)
            .order_by(Resume.id.desc())
            .first()
        )
        if not resume:
            raise ValueError("No original resume found for this user.")
        return resume.extracted_data, None
    
import re

def extract_html_only(text: str) -> str:
    """
    Extracts pure HTML from model output that may be wrapped in markdown fences like ```html ... ```.
    """
    # Case 1: wrapped in ```html ... ```
    match = re.search(r"```(?:html)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Case 2: already plain HTML
    return text.strip()

def render_html_from_image_and_json(
    db: Session,
    username: str,
    image_bytes: bytes,
    filename: str,
    source: str = "original",
    customization_id: Optional[int] = None
) -> dict:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError("User not found.")

    resume_json, used_customization_id = _get_resume_json_for_user(
        db, user, source, customization_id
    )

    data_uri = _encode_image_to_data_uri(image_bytes, filename)

    # Build prompt messages
    prompt = HTML_PROMPT_TMPL.format_messages(resume_json=resume_json)

    system_message = SystemMessage(content=prompt[0].content)
    human_message = HumanMessage(
        content=[
            {"type": "text", "text": prompt[1].content},
            {"type": "image_url", "image_url": data_uri},
        ]
    )

    # Call Gemini
    result = vision_model.invoke([system_message, human_message])
    html = result.content
    html = extract_html_only(html)

    return {
        "html": html,
        "source": source,
        "customization_id": used_customization_id,
    }
