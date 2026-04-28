import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="BA Learning System", layout="wide")

# =============================
# LOAD EXCEL
# =============================
@st.cache_data
def load_excel(file):
    xl = pd.ExcelFile(file)
    questions = xl.parse("Sheet1")
    dataset = xl.parse("Sheet2")
    mapping = xl.parse("Sheet3")
    explanations = xl.parse("explanations")
    return questions, dataset, mapping, explanations

# =============================
# SESSION INIT
# =============================
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0

if "answered" not in st.session_state:
    st.session_state.answered = False

if "correct" not in st.session_state:
    st.session_state.correct = None

# =============================
# UI HEADER
# =============================
st.title("📊 Business Analytics Learning System")

uploaded_file = st.file_uploader("Upload Excel Question Bank")

if uploaded_file:
    questions, df, mapping, explanations = load_excel(uploaded_file)
    st.session_state.loaded = True

if not st.session_state.loaded:
    st.stop()

# =============================
# CREATE MAPPING
# =============================
name_map = dict(zip(mapping["Internal"], mapping["Display"]))

# =============================
# DISPLAY DATASET
# =============================
st.subheader("📊 Dataset Preview")
df_display = df.rename(columns=name_map)
st.dataframe(df_display.head(15))

csv = df_display.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download Full Dataset", csv, "dataset.csv")

st.info("⚠️ Use FULL dataset for calculations (Jamovi)")

# =============================
# SELECT QUESTION
# =============================
q = questions.iloc[st.session_state.q_idx]

# Replace internal names with display names
question_text = q["QuestionText"]
for k, v in name_map.items():
    question_text = question_text.replace(k, v)

st.subheader("Current Question")
st.write(question_text)

# =============================
# INPUT
# =============================
if q["AnswerType"] == "numeric":
    user_ans = st.number_input("Enter answer", format="%.5f")
else:
    options = [q["Option1"], q["Option2"], q["Option3"], q["Option4"]]
    options = [o for o in options if pd.notna(o)]
    user_ans = st.radio("Select answer", options)

# =============================
# SUBMIT
# =============================
if st.button("Submit") and not st.session_state.answered:

    correct_ans = q["CorrectAnswer"]

    if q["AnswerType"] == "numeric":
        tol = q.get("Tolerance", 0.01)
        correct = abs(user_ans - correct_ans) <= tol
    else:
        correct = user_ans == q["CorrectOption"]

    st.session_state.correct = correct
    st.session_state.answered = True

# =============================
# RESULT
# =============================
if st.session_state.answered:

    if st.session_state.correct:
        st.success("Correct ✅")
    else:
        st.error("Incorrect ❌")
        st.write(f"Your answer: {user_ans}")
        st.write(f"Correct answer: {q['CorrectAnswer']}")

    # =============================
    # EXPLANATION
    # =============================
    st.markdown("### 🔍 Explanation")

    exp = explanations[explanations["QuestionID"] == q["QuestionID"]]

    if not exp.empty:
        st.write(exp.iloc[0]["ExplanationText"])
    else:
        st.write(q.get("Explanation", "No explanation available"))

    # =============================
    # NEXT QUESTION
    # =============================
    if st.button("Next Question"):
        st.session_state.q_idx += 1
        st.session_state.answered = False
        st.session_state.correct = None

        if st.session_state.q_idx >= len(questions):
            st.session_state.q_idx = 0

        st.rerun()
