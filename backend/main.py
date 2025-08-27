import os
from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine, Base
from models import User, Resume, ResumeCustomization
from auth import hash_password, verify_password
from extract_resume_data import extract_data_from_resume
from change_resume_json import change_resume_json
import tempfile
from vision_renderer import render_html_from_image_and_json


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(username=username, password=hash_password(password))
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful", "username": username}


# --- Dummy resume processor ---
def process_resume(file_path: str) -> dict:
    return extract_data_from_resume(file_path)



@app.post("/upload_resume")
async def upload_resume(username: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    extracted = process_resume(file_location)

    resume = Resume(filename=file.filename, extracted_data=extracted, owner=user)
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {"message": "Resume uploaded successfully", "extracted_data": extracted}

@app.post("/customize_resume")
def customize_resume(username: str = Form(...), job_post: str = Form(...), db: Session = Depends(get_db)):
    # 1. Find user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Get latest resume
    resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.id.desc()).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found for this user")

    # 3. Prepare prompt
    updated_json = change_resume_json(resume.extracted_data, job_post)

    customization = ResumeCustomization(
        job_post_text=job_post,
        customized_data=updated_json,
        resume=resume,
        user=user
    )

    db.add(customization)
    db.commit()
    db.refresh(customization)

    # 5. Return updated JSON
    return {
        "message": "Customized resume saved successfully",
        "customized_resume": updated_json,
        "customization_id": customization.id
    }

@app.get("/get_customized_resumes")
def get_customized_resumes(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    customizations = db.query(ResumeCustomization).filter(ResumeCustomization.user_id == user.id).all()

    return {
        "customizations": [
            {
                "id": c.id,
                "job_post_text": c.job_post_text,
                "customized_data": c.customized_data
            }
            for c in customizations
        ]
    }


@app.post("/render_resume_from_image")
async def render_resume_from_image(
    username: str = Form(...),
    source: str = Form("original"),  # "original" or "customized"
    customization_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        image_bytes = await file.read()
        out = render_html_from_image_and_json(
            db=db,
            username=username,
            image_bytes=image_bytes,
            filename=file.filename,
            source=source,
            customization_id=customization_id
        )

        html_text = out["html"]

        # ---- Convert HTML to PDF ----
        from vision_renderer import html_to_pdf_bytes
        pdf_bytes = html_to_pdf_bytes(html_text)

        # Save to tmp file
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmpfile.write(pdf_bytes)
        tmpfile.flush()
        tmpfile.close()

        return {
            "message": "Rendered successfully",
            "html": html_text,
            "pdf_url": f"/download_pdf/{os.path.basename(tmpfile.name)}",
            "source": out["source"],
            "customization_id": out["customization_id"],
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Rendering failed: {e}")


@app.get("/download_pdf/{filename}")
def download_pdf(filename: str):
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(tmp_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(tmp_path, media_type="application/pdf", filename="resume.pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)