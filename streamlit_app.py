import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics Learning System", layout="wide")

# -----------------------------
# SESSION INIT
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "question" not in st.session_state:
    st.session_state.question = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "correct" not in st.session_state:
    st.session_state.correct = None

# -----------------------------
# DATASET GENERATOR
# -----------------------------
def generate_dataset():
    np.random.seed()

    n = 120

    heart_rate = np.random.normal(72, 8, n)
    gender = np.random.choice(["Male", "Female"], n)

    # Create relationship: higher HR → slightly higher temp
    body_temp = 97 + (heart_rate - 70)*0.03 + np.random.normal(0, 0.3, n)

    df = pd.DataFrame({
        "HeartRate": np.round(heart_rate, 0),
        "BodyTemp": np.round(body_temp, 3),
        "Gender": gender
    })

    return df

# -----------------------------
# QUESTION GENERATOR
# -----------------------------
def generate_question(df):

    # Always recompute grouping from THIS dataset
    g1 = df[df["HeartRate"] > 75]["BodyTemp"]
    g2 = df[df["HeartRate"] <= 75]["BodyTemp"]

    # Normality
    p1 = stats.shapiro(g1)[1]
    p2 = stats.shapiro(g2)[1]

    # Variance
    lev_p = stats.levene(g1, g2)[1]

    # Decision logic (Jamovi style)
    if p1 > 0.05 and p2 > 0.05:
        if lev_p > 0.05:
            test = "Student t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=True)
        else:
            test = "Welch t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=False)
    else:
        test = "Mann-Whitney U"
        stat, pval = stats.mannwhitneyu(g1, g2)

    return {
        "question": "Split data:\n\nGroup 1: HeartRate > 75\nGroup 2: HeartRate ≤ 75\n\nTest if BodyTemp differs.\n\nEnter p-value (approx):",
        "type": "numeric",
        "answer": round(pval, 4),
        "test": test,
        "p1": p1,
        "p2": p2,
        "lev_p": lev_p
    }

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Business Analytics Learning System")

student = st.text_input("Student Name", "ABC123")

# -----------------------------
# START SESSION
# -----------------------------
if st.button("🚀 Start New Session"):

    st.session_state.df = generate_dataset()
    st.session_state.question = generate_question(st.session_state.df)

    st.session_state.answered = False
    st.session_state.correct = None

    st.success("New dataset generated for this session")

# -----------------------------
# SHOW DATASET
# -----------------------------
if st.session_state.df is not None:

    st.subheader("Dataset (Use this for analysis)")
    st.dataframe(st.session_state.df.head(15), use_container_width=True)

# -----------------------------
# QUESTION BLOCK
# -----------------------------
if st.session_state.question:

    q = st.session_state.question

    st.subheader("Current Question")
    st.write(q["question"])

    user_ans = st.number_input("Enter answer", value=0.0)

    # -----------------------------
    # SUBMIT
    # -----------------------------
    if st.button("Submit"):

        tol = 0.02

        st.session_state.correct = abs(user_ans - q["answer"]) <= tol
        st.session_state.answered = True

        st.rerun()

# -----------------------------
# RESULT
# -----------------------------
if st.session_state.answered:

    q = st.session_state.question

    if st.session_state.correct:
        st.success("Correct ✅")
    else:
        st.error("Incorrect ❌")
        st.write(f"Your answer: {user_ans}")
        st.write(f"Correct answer: {q['answer']}")

    # -----------------------------
    # EXPLANATION
    # -----------------------------
    st.markdown("### 🔍 Explanation")

    st.write(f"""
Normality p-values:
- Group 1: {round(q['p1'],4)}
- Group 2: {round(q['p2'],4)}

Levene test p-value: {round(q['lev_p'],4)}

👉 Selected Test: {q['test']}

👉 Final p-value: {q['answer']}

Interpretation:
If p < 0.05 → significant difference  
If p ≥ 0.05 → no significant difference
""")

    # -----------------------------
    # NEXT QUESTION
    # -----------------------------
    if st.button("Next Question"):

        st.session_state.question = generate_question(st.session_state.df)
        st.session_state.answered = False
        st.session_state.correct = None

        st.rerun()
