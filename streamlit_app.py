import streamlit as st
import pandas as pd
import numpy as np
import random
from scipy import stats
from openai import OpenAI

# -----------------------
# OPENAI CLIENT
# -----------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------
# DATASET GENERATION
# -----------------------
np.random.seed(42)
n = 120

df = pd.DataFrame({
    "Sales": np.random.normal(200, 50, n),
    "Cost": np.random.normal(120, 30, n),
    "Marketing": np.random.normal(60, 20, n),
    "Satisfaction": np.random.normal(70, 10, n),
    "Delivery_Time": np.random.normal(5, 1.5, n),
    "Region": np.random.choice(["North", "South", "East"], n),
    "Segment": np.random.choice(["Retail", "Corporate", "SME"], n),
    "Channel": np.random.choice(["Online", "Offline"], n)
})

# -----------------------
# MODULE FLOW
# -----------------------
modules = ["Descriptive Stats", "Hypothesis Testing", "ANOVA", "Regression"]

# -----------------------
# SESSION STATE INIT
# -----------------------
if "module" not in st.session_state:
    st.session_state.module = 0

if "question" not in st.session_state:
    st.session_state.question = None

if "answered_correct" not in st.session_state:
    st.session_state.answered_correct = False

# -----------------------
# AI QUESTION GENERATOR
# -----------------------
def generate_ai_question(module, difficulty):
    prompt = f"""
    You are a statistics professor.

    Generate a {difficulty} level question for {module}.

    RULES:
    - Do NOT give answers in the question
    - Use realistic business context
    - Require interpretation or calculation
    - Avoid trivial questions
    - Provide:
        1. question
        2. numeric answer
        3. detailed explanation

    Format:
    QUESTION:
    ...
    ANSWER:
    ...
    EXPLANATION:
    ...
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    text = response.choices[0].message.content

    try:
        q = text.split("QUESTION:")[1].split("ANSWER:")[0].strip()
        ans = float(text.split("ANSWER:")[1].split("EXPLANATION:")[0].strip())
        exp = text.split("EXPLANATION:")[1].strip()
    except:
        q, ans, exp = text, 0, "Parsing error"

    return {"q": q, "answer": ans, "explanation": exp}

# -----------------------
# FALLBACK (NON-AI)
# -----------------------
def fallback_question(module, difficulty):

    if module == "Descriptive Stats":
        x = df["Sales"]
        y = df["Cost"]

        if difficulty == "Easy":
            return {
                "q": "Which variable has higher variability: Sales or Cost?",
                "options": ["Sales", "Cost"],
                "answer": "Sales",
                "explanation": "Compare standard deviations."
            }

        elif difficulty == "Medium":
            subset = df[df["Region"] == "East"]["Sales"]
            mean = subset.mean()
            sd = subset.std()
            val = mean - sd

            prob = stats.norm.cdf(val, mean, sd)

            return {
                "q": f"For Region = East, compute P(Sales < {round(val,2)}).",
                "answer": round(prob, 2),
                "explanation": "Compute mean & SD, then use normal CDF."
            }

        else:
            return {
                "q": "Compare skewness of Sales and Marketing and interpret.",
                "answer": 0,
                "explanation": "Higher skew means asymmetry."
            }

    return generate_ai_question(module, difficulty)

# -----------------------
# UI
# -----------------------
st.title("📊 Business Analytics Learning System")

name = st.text_input("Student Name")
difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])

current_module = modules[st.session_state.module]
st.subheader(f"Current Module: {current_module}")

# -----------------------
# GENERATE QUESTION
# -----------------------
if st.session_state.question is None or st.session_state.answered_correct:
    try:
        q = generate_ai_question(current_module, difficulty)
    except:
        q = fallback_question(current_module, difficulty)

    st.session_state.question = q
    st.session_state.answered_correct = False

# -----------------------
# DISPLAY QUESTION
# -----------------------
q = st.session_state.question
st.write(q["q"])

# -----------------------
# ANSWER INPUT
# -----------------------
user_ans = st.number_input("Your Answer", value=0.0)

if st.button("Submit"):

    correct = False

    try:
        correct = abs(user_ans - float(q["answer"])) < 0.1
    except:
        correct = False

    if correct:
        st.success("✅ Correct!")

        st.session_state.answered_correct = True

        # move module forward if needed
        if random.random() > 0.6:
            st.session_state.module += 1

            if st.session_state.module >= len(modules):
                st.success("🎓 You completed all modules!")
                st.stop()

    else:
        st.error("❌ Incorrect")

        st.write("### Detailed Explanation:")
        st.write(q["explanation"])

        # keep same question (adaptive loop)
        st.session_state.answered_correct = False
