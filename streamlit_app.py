import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import random

st.set_page_config(layout="wide")

# -------------------------
# VERSION CHECK
# -------------------------
st.write("VERSION: CLEAN BUILD V1")

# -------------------------
# DATASET
# -------------------------
np.random.seed(42)

n = 120
df = pd.DataFrame({
    "body_temp": np.random.normal(98.2, 0.7, n),
    "heart_rate": np.random.normal(72, 10, n),
    "age": np.random.randint(20, 60, n),
    "region": np.random.choice(["North","South","East"], n)
})

# -------------------------
# MODULES
# -------------------------
modules = [
    "Descriptive Stats",
    "Hypothesis Testing",
    "ANOVA",
    "Regression"
]

# -------------------------
# SESSION STATE
# -------------------------
if "module" not in st.session_state:
    st.session_state.module = 0

if "question" not in st.session_state:
    st.session_state.question = None

if "correct" not in st.session_state:
    st.session_state.correct = False

# -------------------------
# DESCRIPTIVE ENGINE
# -------------------------
def descriptive_engine():

    var = random.choice(["body_temp","heart_rate"])
    region = random.choice(df["region"].unique())
    subset = df[df["region"] == region]

    qtype = random.choice(["variability","observed_prob"])

    if qtype == "variability":

        sd1 = subset["body_temp"].std()
        sd2 = subset["heart_rate"].std()

        correct = "body_temp" if sd1 > sd2 else "heart_rate"

        return {
            "q": f"""
Filter data where region = {region}.

Which variable has higher variability?
""",
            "type":"mcq",
            "options":["body_temp","heart_rate"],
            "answer":correct,
            "explanation":"Compare standard deviations (higher SD ⇒ higher variability)"
        }

    else:

        mean_val = subset[var].mean()
        observed = (subset[var] < mean_val).mean()

        return {
            "q": f"""
Filter data where region = {region}.

Compute observed probability:

P({var} < mean)
""",
            "type":"numeric",
            "answer": round(observed,2),
            "explanation":"Count number of observations below mean / total"
        }

# -------------------------
# HYPOTHESIS ENGINE
# -------------------------
def hypothesis_engine():

    scenario = random.choice(["one_sample","two_sample"])

    if scenario == "one_sample":

        sample = df["body_temp"]
        t_stat, p_val = stats.ttest_1samp(sample, 98)

        return {
            "q": """
Test whether mean body temperature is significantly different from 98.

Enter p-value (approx)
""",
            "type":"numeric",
            "answer": round(p_val,3),
            "explanation":"Use one-sample t-test"
        }

    else:

        g1 = df[df["heart_rate"] > 75]["body_temp"]
        g2 = df[df["heart_rate"] <= 75]["body_temp"]

        t_stat, p_val = stats.ttest_ind(g1, g2)

        return {
            "q": """
Split data:

Group 1: heart_rate > 75  
Group 2: heart_rate ≤ 75  

Test if body temperature differs.

Enter p-value (approx)
""",
            "type":"numeric",
            "answer": round(p_val,3),
            "explanation":"Use independent t-test"
        }

# -------------------------
# ANOVA ENGINE
# -------------------------
def anova_engine():

    groups = [
        df[df["region"]=="North"]["body_temp"],
        df[df["region"]=="South"]["body_temp"],
        df[df["region"]=="East"]["body_temp"]
    ]

    f_stat, p_val = stats.f_oneway(*groups)

    return {
        "q": """
Compare body temperature across regions.

Perform ANOVA.

Enter p-value (approx)
""",
        "type":"numeric",
        "answer": round(p_val,3),
        "explanation":"ANOVA compares means across groups"
    }

# -------------------------
# REGRESSION ENGINE
# -------------------------
def regression_engine():

    corr = df["body_temp"].corr(df["heart_rate"])

    return {
        "q": """
Compute correlation between body temperature and heart rate.

Enter value (approx)
""",
        "type":"numeric",
        "answer": round(corr,2),
        "explanation":"Correlation measures linear relationship"
    }

# -------------------------
# ROUTER
# -------------------------
def get_question():

    module = modules[st.session_state.module]

    if module == "Descriptive Stats":
        return descriptive_engine()

    elif module == "Hypothesis Testing":
        return hypothesis_engine()

    elif module == "ANOVA":
        return anova_engine()

    else:
        return regression_engine()

# -------------------------
# UI
# -------------------------
st.title("📊 Business Analytics Learning System")

st.subheader(f"Module: {modules[st.session_state.module]}")

# Generate question
if st.session_state.question is None or st.session_state.correct:
    st.session_state.question = get_question()
    st.session_state.correct = False

q = st.session_state.question

# Safety
if "type" not in q:
    q["type"] = "mcq"

st.write(q["q"])

# Input
if q["type"] == "numeric":
    user_ans = st.number_input("Enter Answer", value=0.0, step=0.01)
else:
    user_ans = st.radio("Select answer:", q["options"])

# -------------------------
# EVALUATION
# -------------------------
if st.button("Submit"):

    if q["type"] == "numeric":
        correct = abs(user_ans - q["answer"]) < 0.05
    else:
        correct = user_ans == q["answer"]

    if correct:
        st.success("✅ Correct")
    
        st.session_state.question = None
        st.session_state.correct = True
    
        st.rerun()
        # progress randomly
        if random.random() > 0.6:
            st.session_state.module += 1

            if st.session_state.module >= len(modules):
                st.success("🎓 You completed all modules!")
                st.stop()

    else:
        st.error("❌ Incorrect")

        st.write("### Explanation")
        st.write(q["explanation"])

        st.session_state.correct = False
