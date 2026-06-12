# 📄 Resume Analyzer / Job Matcher

A simple, lightweight web app that analyzes resumes against a job description, ranks them by relevance, checks skill match, and performs an ATS (Applicant Tracking System) compatibility check — all from a clean Streamlit interface.

## ✨ Features

- **Bulk Resume Upload** — Upload multiple resumes at once (PDF, DOCX, or TXT)
- **Job Description Matching** — Computes a similarity score between each resume and the job description using TF-IDF and cosine similarity
- **Skill Matching** — Detects relevant skills in the job description and checks which ones each resume covers, listing both matched and missing skills
- **ATS Compatibility Check** — Scores each resume out of 100 based on:
  - Resume length
  - Presence of email and phone number
  - Key sections (Experience, Education, Skills, Projects)
  - Use of bullet points
- **Ranking Summary** — Resumes are automatically ranked by match percentage
- **Detailed Per-Resume Reports** — Expandable sections with scores, skill breakdowns, and ATS improvement suggestions

## 🛠️ Tech Stack

- **Python**
- **Streamlit** — UI framework
- **Pandas** — Data handling
- **Scikit-learn** — TF-IDF vectorization & cosine similarity
- **PyPDF2** — PDF text extraction
- **docx2txt** — DOCX text extraction

## 📦 Installation

1. Clone or download this project.

2. Install dependencies:
```bash
   pip install -r requirements.txt
```

3. Run the app:
```bash
   streamlit run app.py
```

4. Open the local URL shown in your terminal (usually `http://localhost:8501`).

## 🚀 How to Use

1. Paste the **Job Description** into the text box.
2. Upload one or more **resumes** (PDF, DOCX, or TXT format).
3. Click **🔍 Analyze Resumes**.
4. View:
   - A summary table ranking resumes by match percentage
   - Skills detected in the job description
   - Per-resume details: match %, ATS score, matched/missing skills, and improvement suggestions

## 📋 Requirements
streamlit
pandas
scikit-learn
PyPDF2
docx2txt

## ⚙️ How It Works

1. **Text Extraction** — Extracts raw text from uploaded resumes (PDF/DOCX/TXT).
2. **Job Match Score** — Both the job description and resumes are vectorized using TF-IDF; cosine similarity gives the overall match percentage.
3. **Skill Matching** — A curated skill database is checked against both the job description and each resume using normalized text matching (handles formatting differences, punctuation, and word boundaries).
4. **ATS Score** — Each resume is evaluated against common ATS-friendly formatting rules and given a score out of 100, with feedback on what to improve.

## 📝 Customization

To improve skill detection accuracy for your domain, edit the `COMMON_SKILLS` list in `app.py` and add relevant skills, tools, or technologies.

## 📄 License

Free to use and modify for personal or educational purposes.