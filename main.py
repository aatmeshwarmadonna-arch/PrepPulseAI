import streamlit as st
import json
import PyPDF2
from gemini import ask_gemini  # Ensure gemini.py is in the same folder

# 1. LOAD DATA FILES
@st.cache_data
def load_data():
    try:
        with open("companies.json") as f:
            companies = json.load(f)
        with open("curriculum.json") as f:
            curr = json.load(f)
        return companies, curr
    except FileNotFoundError:
        return [], {}

COMPANIES, curriculum = load_data()

# 2. PAGE CONFIG
st.set_page_config(page_title="Placement Guidance System", layout="wide")

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align: center;'>Placement Guidance System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>AI-Powered Career & Resume Analysis</p><hr>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.header("Student Profile")
year = st.sidebar.selectbox("Academic Year", ["Select", "1st Year", "2nd Year", "3rd Year", "4th Year"])
cgpa = st.sidebar.number_input("CGPA", 0.0, 10.0, step=0.1)
skills_input = st.sidebar.text_input("Skills (comma separated)")
experience = st.sidebar.number_input("Experience (months)", 0, 60)

# ---------------- TABS ----------------
tabs = st.tabs(["🏠 Home", "📄 Resume Checker", "🏢 Companies", "🎯 Placement", "📘 Study Roadmap", "🤖 Mock Interview"])

# Global Variable for Resume Text
resume_text = ""

# ======================================================
# TAB 2: RESUME CHECKER
# ======================================================
with tabs[1]:
    st.subheader("AI Resume Analysis")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded_file:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                resume_text += content
        
        if not resume_text.strip():
            st.error("❌ ERROR: Your PDF is a scanned image. Please upload a Digital PDF.")
        else:
            st.success("✅ Resume text captured!")
            with st.expander("🔍 View Extracted Text"):
                st.text(resume_text)

            st.divider()
            target_company = st.selectbox("Select Company:", [c["company"] for c in COMPANIES])
            
            if st.button("Run AI Deep Comparison"):
                comp_details = next(c for c in COMPANIES if c["company"] == target_company)
                with st.spinner("Analyzing..."):
                    prompt = f"Compare this resume: {resume_text} against these requirements: {json.dumps(comp_details)}"
                    ai_feedback = ask_gemini(prompt)
                    st.markdown(ai_feedback)

# ======================================================
# TAB 5: STUDY ROADMAP
# ======================================================
with tabs[4]:
    st.subheader("🎓 Personalized AI Study Roadmap")
    if not resume_text:
        st.warning("Please upload your resume in the 'Resume Checker' tab first.")
    else:
        target_study_company = st.selectbox("Target Company for Roadmap:", [c["company"] for c in COMPANIES], key="study_comp")
        duration = st.slider("Preparation Duration (Weeks):", 1, 12, 4)

        if st.button("Generate My Study Plan"):
            comp_details = next(c for c in COMPANIES if c["company"] == target_study_company)
            with st.spinner("Generating roadmap..."):
                study_prompt = f"Create a {duration}-week study plan for {target_study_company} based on this resume: {resume_text[:2000]}. Requirements: {json.dumps(comp_details)}"
                roadmap = ask_gemini(study_prompt)
                st.markdown(roadmap)

# ======================================================
# TAB 6: MOCK INTERVIEW
# ======================================================
with tabs[5]:
    st.subheader("🤖 AI Mock Interviewer")
    if not resume_text:
        st.warning("Please upload your resume first.")
    else:
        interview_company = st.selectbox("Company to Interview for:", [c["company"] for c in COMPANIES], key="int_comp")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if st.button("Start New Interview"):
            st.session_state.chat_history = []
            comp_info = next(c for c in COMPANIES if c["company"] == interview_company)
            initial_prompt = f"Interview the student for {interview_company}. Resume: {resume_text[:1000]}. Start with one question."
            first_msg = ask_gemini(initial_prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": first_msg})

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if user_answer := st.chat_input("Your answer..."):
            st.session_state.chat_history.append({"role": "human", "content": user_answer})
            with st.chat_message("user"): st.write(user_answer)
            
            with st.spinner("Interviewer is thinking..."):
                follow_up_prompt = f"Previous Chat: {st.session_state.chat_history[-2:]}. Answer: {user_answer}. Give feedback and ask the next question."
                next_msg = ask_gemini(follow_up_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": next_msg})
                st.rerun()

# ======================================================
# REMAINING TABS
# ======================================================
with tabs[0]: st.write("Welcome! Start by uploading your resume.")
with tabs[2]: st.table(COMPANIES)
with tabs[3]: st.write("Eligibility based on sidebar profile.")