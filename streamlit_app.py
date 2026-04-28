import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from openai import OpenAI

# -----------------------------
# OPENAI
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ai_explain(context):
    prompt = f"""
You are a statistics professor teaching undergraduate business students.

Explain the following result in SIMPLE terms:

{context}

- No jargon
- Step-by-step
- Explain decision (reject / not reject)
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# -----------------------------
# PAGE
# -----------------------------
st.set_page_config(page_title="Business Analytics Learning System", layout="wide")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
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
def generate_descriptive_question():
    df = st.session_state.df

    col = np.random.choice(["HeartRate", "BodyTemp"])
    mean_val = df[col].mean()

    return {
        "question": f"What is the approximate mean of {col}?",
        "type": "numeric",
        "answer": round(mean_val, 2),
        "explanation": f"Mean of {col} = {round(mean_val,2)}"
    }

def generate_hypothesis_question():
    df = st.session_state.df

    g1 = df[df["HeartRate"] > 75]["BodyTemp"]
    g2 = df[df["HeartRate"] <= 75]["BodyTemp"]

    p1 = stats.shapiro(g1)[1]
    p2 = stats.shapiro(g2)[1]
    lev_p = stats.levene(g1, g2)[1]

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

    decision = "Reject H0" if pval < 0.05 else "Fail to reject H0"

    return {
        "question": """
You ran an independent samples test in Jamovi.

Group 1: HeartRate > 75  
Group 2: HeartRate ≤ 75  

👉 What is the correct conclusion?
""",
        "type": "mcq",
        "options": [
            "Reject H0: Body temperature differs",
            "Fail to reject H0: No difference",
            "Use regression instead",
            "Cannot conclude"
        ],
        "answer": "Reject H0: Body temperature differs" if pval < 0.05 else "Fail to reject H0: No difference",
        "context": f"""
Test: {test}
p-value: {round(pval,4)}
Normality p-values: {round(p1,4)}, {round(p2,4)}
Levene p-value: {round(lev_p,4)}
Decision: {decision}
"""
    }

def generate_regression_question():
    df = st.session_state.df

    x = df["HeartRate"]
    y = df["BodyTemp"]

    import statsmodels.api as sm

    X = sm.add_constant(df["HeartRate"])
    y = df["BodyTemp"]
    
    model = sm.OLS(y, X).fit()
    slope = model.params["HeartRate"]
    p_value = model.pvalues["HeartRate"]

    return {
        "question": "What is the slope of regression: BodyTemp ~ HeartRate?",
        "type": "numeric",
        "answer": round(slope, 3),
        "explanation": f"""
        Using OLS regression (same as Jamovi):
        
        Slope ≈ {round(slope,3)}
        p-value ≈ {round(p_value,4)}
        
        Interpretation:
        Each 1 unit increase in HeartRate increases BodyTemp by ~{round(slope,3)}.
        """
    }

# -----------------------------
# QUESTION ROUTER
# -----------------------------
def generate_question():
    module = np.random.choice(["descriptive", "hypothesis", "regression"])

    if module == "descriptive":
        return generate_descriptive_question()
    elif module == "hypothesis":
        return generate_hypothesis_question()
    else:
        return generate_regression_question()

# -----------------------------
# UI
# -----------------------------
st.title("📊 Business Analytics Learning System")

student = st.text_input("Student Name", "ABC123")

# -----------------------------
# START SESSION
# -----------------------------
if st.button("🚀 Start New Session"):

    st.session_state.df = generate_dataset()
    st.session_state.question = generate_question()
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
# SHOW QUESTION
# -----------------------------
if st.session_state.question:

    q = st.session_state.question

    # 🔥 SHOW JAMOVI STYLE OUTPUT
    if "context" in q:
        st.markdown("### 📊 Jamovi Output (Simplified)")
        st.code(q["context"])

    st.subheader("Current Question")
    st.write(q["question"])

    if q["type"] == "numeric":
        user_ans = st.number_input("Enter answer", value=0.0)
    else:
        user_ans = st.radio("Select answer", q["options"])

    if st.button("Submit"):

        if q["type"] == "numeric":
            correct = abs(user_ans - q["answer"]) <= 0.05
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

    if "ai_explanation" not in st.session_state:
        st.session_state.ai_explanation = None
    
    # Only generate ONCE
    if st.session_state.ai_explanation is None:
    
        try:
            if "context" in q:
                st.session_state.ai_explanation = ai_explain(q["context"])
            else:
                st.session_state.ai_explanation = q["explanation"]
    
        except Exception:
            st.session_state.ai_explanation = "⚠️ Explanation temporarily unavailable. Please retry."
    
    st.write(st.session_state.ai_explanation)
    # 🔥 AI explanation for hypothesis
    if "context" in q:
        explanation = ai_explain(q["context"])
    else:
        explanation = q["explanation"]

    st.write(explanation)

    # -----------------------------
    # NEXT QUESTION
    # -----------------------------
    if st.button("Next Question"):

        st.session_state.question = generate_question()
        st.session_state.answered = False
        st.session_state.correct = None
        st.session_state.ai_explanation = None   # 🔥 IMPORTANT RESET
    
        st.rerun()
