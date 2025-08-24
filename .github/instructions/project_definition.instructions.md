You are assisting in a multi-agent AI system that improves job applications by generating tailored resumes.

The project is called: **Recruiter Agent for Resume Matching**

### 🔍 Project Objective:
To automate the process of matching a candidate's resume to a specific job post and generate multiple optimized resume variants to increase the chances of getting shortlisted by ATS systems or recruiters.

---

### 📦 Inputs:
1. **Base Resume (PDF or text)** – original resume from user
2. **Additional Skills or Info** – extra tech or domain skills the user wants to highlight
3. **Job Post** – either a job description link (e.g., LinkedIn) or raw job text

---

### 📤 Output:
- 2–3 resume variants tailored to the job post
- Resume score based on keyword match and relevance
- PDF and DOCX files for download
- Resume improvement suggestions

---

### ⚙️ System Workflow (Simplified):
1. **User Upload**: Resume + skills + job post
2. **Parsing Agents**: Extract info from resume and job
3. **Trending Keywords Agent**: Detect keywords from job post and current market trends
4. **LLM Resume Editor Agent**:
   - Inputs: Resume data + skills + job keywords
   - Outputs: 2–3 optimized resume JSONs
5. **Resume Template Agent**: Fills JSON into pre-defined template (DOCX/HTML)
6. **ATS Scorer Agent**: Evaluates how well resume matches the job
7. **Iteration Agent**: Can create new versions using previous variant history
8. **Export Agent**: Final PDF and DOCX files are generated for download

---

### 💾 Data Storage (MCP Protocol):
- `resume:{user_id}` → original + parsed resume
- `skills:{user_id}` → additional skills
- `job_post:{job_id}` → parsed job description + keywords
- `resume_variant:{user_id}:{job_id}` → variant history with scores

---

### 🧠 Agent Goals:
- Understand resume content and job post requirements
- Add relevant keywords, projects, and soft skills to improve match
- Keep each resume version unique and ATS-optimized
- Allow iteration for multiple resume strategies

---

### ⚙️ Tools Available to Agents:
- LLMs (GPT-4, Claude, Ollama)
- PDF parsing, job scraping, template editing (Word/HTML)
- Vector store or memory (ChromaDB or SQLite)

---

### 🧠 Future Plans:
- Add interview question generation based on resume + job post
- Create email cover letters per resume variant
- Build recruiter feedback loop to learn what works

---
