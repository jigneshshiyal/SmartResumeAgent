# Resume Extractor & Customizer 🚀

A full-stack project for **resume extraction and customization** using FastAPI, SQLAlchemy, LangChain (Gemini), and Streamlit.  

- 📝 Upload resume (PDF/DOCX) → extract structured JSON.  
- 🔑 Login/Register system with user management.  
- 🛠️ Customize resumes with LinkedIn job posts (only updates `skills`).  
- 💾 Save each customization with mapping to original resume + job post.  
- 🌐 Frontend built with Streamlit for easy interaction.  


## 🔧 Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Passlib, LangChain (Gemini API), PyPDF  
- **Frontend**: Streamlit  
- **Database**: SQLite (default, can be replaced with Postgres/MySQL)  


## ⚙️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/resume-customizer.git
cd resume-customizer
````

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Environment

Create a `.env` file in **backend/**:

```
GEMINI_API_KEY=your_gemini_api_key
```


## ▶️ Running the App

### 1. Start Backend

From `backend/`:

```bash
uvicorn main:app --reload --port 8000
```

* API runs at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Start Frontend

From `frontend/`:

```bash
streamlit run app.py
```

* Frontend runs at: [http://localhost:8501](http://localhost:8501)


## 📂 Project Structure

```
resume-customizer/
│
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── auth.py                 # Authentication (hashing, verification)
│   ├── database.py             # DB setup (SQLAlchemy, SQLite)
│   ├── models.py               # User, Resume, ResumeCustomization tables
│   ├── extract_resume_data.py  # Extract resume JSON using Gemini
│   ├── prompt.py               # Prompt template for extraction
│   ├── resume_models.py        # Pydantic models for structured resume
│   └── uploads/                # Uploaded resumes
│
├── frontend/
│   └── app.py                  # Streamlit frontend
│
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```


## 🛠️ Features

* **Register/Login**
  Secure password hashing using Passlib.

* **Upload Resume**
  Upload a PDF/DOCX → Extract structured JSON using Gemini.

* **Customize Resume**
  Provide a LinkedIn job post text → New JSON with updated skills.

* **Save Customizations**
  Each customization saved in `resume_customizations` table with mapping to:

  * Original resume JSON
  * Job post text
  * Customized JSON

* **View Custom Resumes**
  Streamlit page to view all saved customizations.


## 📜 Example Flow

1. Register/Login
2. Upload Resume → Extract JSON (saved in DB).
3. Go to **Customize Resume** → Paste LinkedIn job post text → Backend updates JSON (`skills` only).
4. Customization saved in DB.
5. View all custom resumes from **View Custom Resumes** page.

