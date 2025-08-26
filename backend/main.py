import os
from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine, Base
from models import User, Resume
from auth import hash_password, verify_password
from extract_resume_data import extract_data_from_resume

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)