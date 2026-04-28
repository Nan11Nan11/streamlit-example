import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics Learning System", layout="wide")

# -----------------------------
# STATE INIT
# -----------------------------
modules = ["descriptive", "hypothesis", "regression"]

if "module_index" not in st.session_state:
    st.session_state.module_index = 0
if "question_step" not in st.session_state:
    st.session_state.question_step = 0
if "df" not in st.session_state:
    st.session_state.df = None
if "question" not in st.session_state:
    st.session_state.question = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "correct" not in st.session_state:
    st.session_state.correct = None
if "user_ans" not in st.session_state:
    st.session_state.user_ans = None

# -----------------------------
# DATASET GENERATOR
# -----------------------------
def generate_dataset():
    n = 120
    heart_rate = np.random.normal(72, 8, n)
    gender = np.random.choice(["Male", "Female"], n)
    body_temp = 97 + (heart_rate - 70)*0.03 + np.random.normal(0, 0.3, n)

    df = pd.DataFrame({
        "HeartRate": np.round(heart_rate, 0),
        "BodyTemp": np.round(body_temp, 3),
        "Gender": gender
    })
    return df

# -----------------------------
# QUESTION GENERATORS
# -----------------------------
def generate_descriptive_question(df):
    col = np.random.choice(["HeartRate", "BodyTemp"])
    mean_val = df[col].mean()

    return {
        "question": f"What is the approximate mean of {col}?",
        "type": "numeric",
        "answer": round(mean_val, 2),
        "explanation": f"Mean of {col} = {round(mean_val,2)}"
    }

def generate_hypothesis_question(df):
    g1 = df[df["HeartRate"] > 75]["BodyTemp"]
    g2 = df[df["HeartRate"] <= 75]["BodyTemp"]

    p1 = stats.shapiro(g1)[1]
    p2 = stats.shapiro(g2)[1]
    lev_p = stats.levene(g1, g2)[1]

    if p1 > 0.05 and p2 > 0.05:
        if lev_p > 0.05:
            test = "Student t-test"
            _, pval = stats.ttest_ind(g1, g2, equal_var=True)
        else:
            test = "Welch t-test"
            _, pval = stats.ttest_ind(g1, g2, equal_var=False)
    else:
        test = "Mann-Whitney U"
        _, pval = stats.mannwhitneyu(g1, g2)

    return {
        "question": "Enter approximate p-value for difference in BodyTemp (HR>75 vs ≤75)",
        "type": "numeric",
        "answer": round(pval, 4),
        "explanation": f"Test used: {test}, p-value ≈ {round(pval,4)}"
    }

def generate_regression_question(df):
    x = df["HeartRate"]
    y = df["BodyTemp"]

    slope, _, _, p_value, _ = stats.linregress(x, y)

    return {
        "question": "What is the slope of regression: BodyTemp ~ HeartRate?",
        "type": "numeric",
        "answer": round(slope, 3),
        "explanation": f"Slope = {round(slope,3)}, p-value = {round(p_value,4)}"
    }

# -----------------------------
# ROUTER
# -----------------------------
def generate_question(df, difficulty):
    module = modules[st.session_state.module_index]

    if module == "descriptive":
        return generate_descriptive_question(df)

    elif module == "hypothesis":
        return generate_hypothesis_question(df)

    else:
        return generate_regression_question(df)

# -----------------------------
# UI
# -----------------------------
st.title("📊 Business Analytics Learning System")

student = st.text_input("Student Name", "ABC123")

difficulty = st.selectbox(
    "Select Difficulty",
    ["Easy", "Medium", "Hard"]
)

# -----------------------------
# START SESSION
# -----------------------------
if st.button("🚀 Start New Session"):
    st.session_state.df = generate_dataset()
    st.session_state.module_index = 0
    st.session_state.question_step = 0
    st.session_state.question = generate_question(st.session_state.df, difficulty)
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
# QUESTION
# -----------------------------
if st.session_state.question:
    q = st.session_state.question

    st.subheader("Current Question")
    st.write(q["question"])

    if q["type"] == "numeric":
        user_ans = st.number_input("Enter answer", value=0.0)
    else:
        user_ans = st.radio("Select answer", q["options"])

    if st.button("Submit"):

        if q["type"] == "numeric":
            tol = 0.02
            correct = abs(user_ans - q["answer"]) <= tol
        else:
            correct = user_ans == q["answer"]

        st.session_state.correct = correct
        st.session_state.user_ans = user_ans
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

    st.write(f"Your answer: {st.session_state.user_ans}")
    st.write(f"Correct answer: {q['answer']}")

    st.markdown("### 🔍 Explanation")
    st.write(q["explanation"])

    # -----------------------------
    # NEXT QUESTION + PROGRESSION
    # -----------------------------
    if st.button("Next Question"):

        if st.session_state.correct:
            st.session_state.question_step += 1

            if st.session_state.question_step >= 2:
                st.session_state.module_index += 1
                st.session_state.question_step = 0

                if st.session_state.module_index >= len(modules):
                    st.success("🎓 All modules completed!")
                    st.stop()

        st.session_state.question = generate_question(st.session_state.df, difficulty)
        st.session_state.answered = False
        st.session_state.correct = None

        st.rerun()
