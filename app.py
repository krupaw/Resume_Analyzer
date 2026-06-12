import streamlit as st
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx2txt

st.set_page_config(page_title="Resume Analyzer", layout="wide")

# ---------- Helpers ----------
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    elif file.name.endswith(".docx"):
        return docx2txt.process(file)
    else:
        return file.read().decode("utf-8", errors="ignore")

def normalize_for_matching(text):
    text = text.lower()
    # insert space before/after camelCase boundaries (e.g. "MachineLearning" -> "Machine Learning")
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = text.lower()
    text = re.sub(r'[\n\r\t]+', ' ', text)
    # treat punctuation/symbols as spaces (so "node.js" / "node-js" / "node js" all normalize)
    text = re.sub(r'[^a-z0-9\+\#\.]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_skill(skill):
    skill = skill.lower()
    skill = re.sub(r'[^a-z0-9\+\#\.]', ' ', skill)
    skill = re.sub(r'\s+', ' ', skill).strip()
    return skill

def contains_skill(norm_text, skill):
    norm_skill = normalize_skill(skill)
    if ' ' in norm_skill:
        # multi-word: allow flexible spacing/order doesn't matter, but must appear contiguously
        pattern = r'(?<![a-z0-9])' + r'\s*'.join(re.escape(p) for p in norm_skill.split()) + r'(?![a-z0-9])'
    else:
        pattern = r'(?<![a-z0-9])' + re.escape(norm_skill) + r'(?![a-z0-9])'
    return re.search(pattern, norm_text) is not None

# Master skill list (curated, deterministic)
COMMON_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "nosql",
    "machine learning", "deep learning", "nlp", "natural language processing",
    "data analysis", "data science", "data engineering", "data visualization",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "react", "angular", "vue", "node.js", "express", "django", "flask",
    "fastapi", "html", "css", "rest api", "graphql", "aws", "azure", "gcp",
    "docker", "kubernetes", "git", "github", "ci/cd", "jenkins", "linux",
    "excel", "tableau", "power bi", "spark", "hadoop", "etl", "airflow",
    "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
    "communication", "leadership", "project management", "agile", "scrum",
    "problem solving", "team management", "stakeholder management",
    "testing", "automation", "selenium", "api development", "microservices",
    "computer vision", "statistics", "a/b testing", "data structures",
    "algorithms", "object oriented programming", "cloud computing",
    "devops", "data warehousing", "business intelligence", "r programming"
]

def extract_skills(text):
    norm_text = normalize_for_matching(text)
    return set(skill for skill in COMMON_SKILLS if contains_skill(norm_text, skill))

def clean_text_for_tfidf(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def ats_score(resume_text):
    score = 0
    feedback = []

    word_count = len(resume_text.split())
    if word_count > 200:
        score += 20
    else:
        feedback.append("Resume seems too short (< 200 words).")

    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        score += 15
    else:
        feedback.append("No email address found.")

    if re.search(r'(\+?\d{1,3}[\s-]?)?\d{10}', resume_text):
        score += 15
    else:
        feedback.append("No phone number found.")

    sections = ["experience", "education", "skills", "projects"]
    text_lower = resume_text.lower()
    found_sections = [s for s in sections if s in text_lower]
    score += len(found_sections) * 10
    missing = [s for s in sections if s not in found_sections]
    if missing:
        feedback.append(f"Missing sections: {', '.join(missing)}")

    if "•" in resume_text or "- " in resume_text:
        score += 10
    else:
        feedback.append("Use bullet points for readability.")

    score = min(score, 100)
    return score, feedback

# ---------- UI ----------
st.title("📄 Resume Analyzer / Job Matcher")
st.caption("Upload resumes, match against a job description, and check ATS compatibility")

col1, col2 = st.columns([1, 1])

with col1:
    job_description = st.text_area("Paste Job Description", height=200,
                                     placeholder="Paste the job description here...")

with col2:
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

analyze_btn = st.button("🔍 Analyze Resumes", type="primary")

if analyze_btn:
    if not job_description.strip():
        st.warning("Please paste a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        with st.spinner("Analyzing resumes..."):
            results = []

            jd_skills = extract_skills(job_description)

            corpus = [clean_text_for_tfidf(job_description)]
            raw_texts = []
            names = []

            for file in uploaded_files:
                raw_text = extract_text(file)
                raw_texts.append(raw_text)
                corpus.append(clean_text_for_tfidf(raw_text))
                names.append(file.name)

            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(corpus)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

            for i, name in enumerate(names):
                resume_skills = extract_skills(raw_texts[i])

                if jd_skills:
                    matched = sorted(jd_skills & resume_skills)
                    missing = sorted(jd_skills - resume_skills)
                else:
                    matched = sorted(resume_skills)
                    missing = []

                score, feedback = ats_score(raw_texts[i])

                results.append({
                    "Resume": name,
                    "Match %": round(similarities[i] * 100, 2),
                    "ATS Score": score,
                    "Matched Skills": matched,
                    "Missing Skills": missing,
                    "ATS Feedback": feedback
                })

            results_df = pd.DataFrame(results).sort_values(by="Match %", ascending=False).reset_index(drop=True)

        st.success(f"Analyzed {len(uploaded_files)} resume(s)")

        if jd_skills:
            st.info(f"**Skills detected in Job Description ({len(jd_skills)}):** " + ", ".join(sorted(jd_skills)))
        else:
            st.warning("No recognizable skills found in the Job Description from our skill database. "
                        "Showing each resume's detected skills instead.")

        # Summary table
        st.subheader("📋 Ranking Summary")
        display_df = results_df.copy()
        display_df["Matched Skills"] = display_df["Matched Skills"].apply(lambda x: ", ".join(x) if x else "-")
        display_df["Missing Skills"] = display_df["Missing Skills"].apply(lambda x: ", ".join(x) if x else "-")
        st.dataframe(
            display_df[["Resume", "Match %", "ATS Score", "Matched Skills", "Missing Skills"]],
            use_container_width=True
        )

        # Detailed view per resume
        st.subheader("🔍 Detailed Reports")
        for idx, row in results_df.iterrows():
            with st.expander(f"{row['Resume']} — Match: {row['Match %']}% | ATS Score: {row['ATS Score']}/100"):
                c1, c2 = st.columns(2)

                with c1:
                    st.metric("Job Match", f"{row['Match %']}%")
                    st.metric("ATS Score", f"{row['ATS Score']}/100")
                    if jd_skills:
                        st.metric("Skills Matched", f"{len(row['Matched Skills'])}/{len(jd_skills)}")

                with c2:
                    st.write("**✅ Matched Skills:**")
                    st.write(", ".join(row["Matched Skills"]) if row["Matched Skills"] else "None")
                    st.write("**❌ Missing Skills:**")
                    st.write(", ".join(row["Missing Skills"]) if row["Missing Skills"] else "None")

                if row["ATS Feedback"]:
                    st.write("**ATS Suggestions:**")
                    for f in row["ATS Feedback"]:
                        st.write(f"- {f}")
                else:
                    st.write("✅ ATS check passed with no major issues.")