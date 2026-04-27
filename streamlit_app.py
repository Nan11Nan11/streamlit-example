import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics LMS", layout="wide")

# -------------------------
# SESSION INIT
# -------------------------
if "data" not in st.session_state:
    st.session_state.data = None

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "scores" not in st.session_state:
    st.session_state.scores = {}

# -------------------------
# DATASET GENERATOR
# -------------------------
def generate_dataset(n=120):
    np.random.seed(42)

    df = pd.DataFrame({
        "Marketing_Spend": np.random.normal(50, 10, n),
        "Productivity": np.random.normal(60, 15, n),
        "Satisfaction": np.random.normal(70, 8, n),
        "Cost": np.random.normal(40, 12, n),
        "Market_Share": np.random.normal(30, 5, n),
        "Region": np.random.choice(["North", "South", "East", "West"], n),
        "Segment": np.random.choice(["Retail", "Corporate"], n),
        "Strategy": np.random.choice(["Aggressive", "Conservative"], n),
    })

    # Y variable
    df["Sales_Growth"] = (
        0.5 * df["Marketing_Spend"]
        + 0.3 * df["Satisfaction"]
        - 0.2 * df["Cost"]
        + np.random.normal(0, 5, n)
    )

    return df

# -------------------------
# QUESTION GENERATOR
# -------------------------
def generate_questions(topic, df):

    questions = []

    if topic == "Descriptive Statistics":

        q1 = {
            "id": "Q1",
            "question": "Compute mean of Marketing Spend",
            "answer": round(df["Marketing_Spend"].mean(), 2),
            "marks": 2,
            "type": "numeric",
            "explanation": "Mean = sum of values / number of observations"
        }

        q2 = {
            "id": "Q2",
            "question": "Which measure represents dispersion?",
            "options": ["Mean", "Median", "Standard Deviation"],
            "answer": "Standard Deviation",
            "marks": 1,
            "type": "mcq",
            "explanation": "Standard deviation measures spread of data"
        }

        q3 = {
            "id": "Q3",
            "question": "If mean > median, data is?",
            "options": ["Positively skewed", "Negatively skewed"],
            "answer": "Positively skewed",
            "marks": 1,
            "type": "mcq",
            "explanation": "Mean > median indicates right skew"
        }

        questions = [q1, q2, q3]

    # -------------------------
    elif topic == "Normality":

        stat, p = stats.shapiro(df["Marketing_Spend"])

        q1 = {
            "id": "Q1",
            "question": "Given p-value > 0.05, data is?",
            "options": ["Normal", "Not normal"],
            "answer": "Normal",
            "marks": 2,
            "type": "mcq",
            "explanation": "If p-value > alpha (0.05), we fail to reject normality"
        }

        q2 = {
            "id": "Q2",
            "question": "Which test is used for normality?",
            "options": ["t-test", "Shapiro-Wilk", "Chi-square"],
            "answer": "Shapiro-Wilk",
            "marks": 1,
            "type": "mcq",
            "explanation": "Shapiro-Wilk test is standard for normality"
        }

        q3 = {
            "id": "Q3",
            "question": "Interpret p-value in hypothesis testing",
            "marks": 2,
            "type": "text",
            "answer": "p value is probability of observing data given null hypothesis",
            "explanation": "As per your notes, p-value compares with alpha to decide rejection :contentReference[oaicite:1]{index=1}"
        }

        questions = [q1, q2, q3]

    # -------------------------
    elif topic == "Hypothesis Testing":

        sample = df["Marketing_Spend"].sample(50)
        mean = sample.mean()
        sd = sample.std()
        n = len(sample)

        hypo = 50

        t_val = (mean - hypo) / (sd / np.sqrt(n))
        p_val = stats.t.cdf(t_val, df=n-1)

        q1 = {
            "id": "Q1",
            "question": "State null hypothesis if action is required when mean is lower",
            "options": ["Mean >= Hypothesis", "Mean < Hypothesis"],
            "answer": "Mean >= Hypothesis",
            "marks": 2,
            "type": "mcq",
            "explanation": "Null is always opposite of action condition :contentReference[oaicite:2]{index=2}"
        }

        q2 = {
            "id": "Q2",
            "question": f"Compute t-value approx (mean={round(mean,2)}, sd={round(sd,2)}, n={n}, hypo=50)",
            "answer": round(t_val, 2),
            "marks": 3,
            "type": "numeric",
            "explanation": "t = (mean - hypo) / (sd/sqrt(n))"
        }

        q3 = {
            "id": "Q3",
            "question": "If p-value < 0.05, what do you do?",
            "options": ["Reject null", "Accept null"],
            "answer": "Reject null",
            "marks": 1,
            "type": "mcq",
            "explanation": "If p < alpha → reject null (take action)"
        }

        questions = [q1, q2, q3]

    return questions


# -------------------------
# EVALUATION
# -------------------------
def evaluate(questions, responses):

    total = 0
    max_marks = 0
    feedback = []

    for q in questions:
        max_marks += q["marks"]
        user = responses.get(q["id"], None)

        correct = False

        if q["type"] == "mcq":
            correct = (user == q["answer"])

        elif q["type"] == "numeric":
            try:
                correct = abs(float(user) - q["answer"]) < 0.5
            except:
                correct = False

        elif q["type"] == "text":
            correct = len(user) > 10 if user else False

        marks = q["marks"] if correct else 0
        total += marks

        feedback.append({
            "question": q["question"],
            "your_answer": user,
            "correct_answer": q["answer"],
            "marks": f"{marks}/{q['marks']}",
            "explanation": q["explanation"]
        })

    return total, max_marks, feedback


# -------------------------
# UI
# -------------------------
st.title("📊 Business Analytics LMS")

topic = st.selectbox(
    "Select Topic",
    ["Descriptive Statistics", "Normality", "Hypothesis Testing"]
)

if st.button("Generate Dataset"):
    st.session_state.data = generate_dataset()
    st.success("Dataset Generated")

df = st.session_state.data

if df is not None:

    st.dataframe(df.head())

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Full Dataset", csv, "dataset.csv")

    if st.button("Generate Questions"):
        st.session_state.questions = generate_questions(topic, df)
        st.session_state.answers = {}

    questions = st.session_state.questions

    if questions:

        st.subheader("Quiz")

        for q in questions:

            st.write(f"**{q['id']}. {q['question']}** (Marks: {q['marks']})")

            if q["type"] == "mcq":
                st.session_state.answers[q["id"]] = st.radio(
                    "", q["options"], key=q["id"]
                )

            elif q["type"] == "numeric":
                st.session_state.answers[q["id"]] = st.number_input(
                    "", key=q["id"]
                )

            elif q["type"] == "text":
                st.session_state.answers[q["id"]] = st.text_area(
                    "", key=q["id"]
                )

        if st.button("Submit Quiz"):

            total, max_marks, feedback = evaluate(
                questions, st.session_state.answers
            )

            st.success(f"Score: {total}/{max_marks}")

            st.subheader("Detailed Feedback")

            for f in feedback:
                st.write("------")
                st.write("Q:", f["question"])
                st.write("Your Answer:", f["your_answer"])
                st.write("Correct Answer:", f["correct_answer"])
                st.write("Marks:", f["marks"])
                st.write("Explanation:", f["explanation"])
