import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics LMS", layout="wide")

# -----------------------------
# DATASET
# -----------------------------
def generate_dataset(seed=42):
    np.random.seed(seed)

    df = pd.DataFrame({
        "Marketing": np.random.normal(50, 10, 120),
        "Productivity": np.random.normal(60, 15, 120),
        "Satisfaction": np.random.normal(70, 8, 120),
        "Cost": np.random.normal(40, 12, 120),
        "Market_Share": np.random.normal(30, 5, 120),
        "Region": np.random.choice(["North","South","East","West"],120),
        "Segment": np.random.choice(["Retail","Corporate"],120),
        "Strategy": np.random.choice(["Aggressive","Conservative"],120)
    })

    df["Sales"] = (
        0.5*df["Marketing"] +
        0.3*df["Satisfaction"] -
        0.2*df["Cost"] +
        np.random.normal(0,5,120)
    )

    return df

# -----------------------------
# SESSION INIT
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = generate_dataset()

if "current_q" not in st.session_state:
    st.session_state.current_q = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "total" not in st.session_state:
    st.session_state.total = 0


df = st.session_state.df

st.title("📊 Business Analytics Learning Agent")

topic = st.selectbox("Select Topic", [
    "Descriptive",
    "Normality",
    "Subset Analysis",
    "Probability",
    "Hypothesis Testing"
])

# -----------------------------
# QUESTION GENERATOR
# -----------------------------
# -----------------------------
# MEMORY-AWARE QUESTION ENGINE
# -----------------------------
def generate_question(topic, df):

    if "history" not in st.session_state:
        st.session_state.history = []

    vars_num = ["Marketing","Cost","Satisfaction","Productivity","Market_Share"]
    concepts = ["mean","sd","cv","skew","subset","compare","prob"]

    # Avoid repetition
    for _ in range(20):

        var = np.random.choice(vars_num)
        concept = np.random.choice(concepts)

        signature = f"{topic}-{var}-{concept}"

        if signature not in st.session_state.history:
            st.session_state.history.append(signature)
            if len(st.session_state.history) > 20:
                st.session_state.history.pop(0)
            break

    # -----------------------------
    # DESCRIPTIVE
    # -----------------------------
    if topic == "Descriptive":

        if concept == "mean":
            return {
                "q": f"Compute mean of {var}",
                "type": "numeric",
                "answer": df[var].mean(),
                "explanation": "Mean = average"
            }

        if concept == "sd":
            return {
                "q": f"Compute standard deviation of {var}",
                "type": "numeric",
                "answer": df[var].std(),
                "explanation": "SD measures dispersion"
            }

        if concept == "cv":
            return {
                "q": f"Compute coefficient of variation of {var}",
                "type": "numeric",
                "answer": df[var].std()/df[var].mean(),
                "explanation": "CV = SD / Mean"
            }

        if concept == "compare":
            v2 = np.random.choice(vars_num)
            return {
                "q": f"Which has higher variability: {var} or {v2}?",
                "type": "mcq",
                "options": [var, v2],
                "answer": var if df[var].std() > df[v2].std() else v2,
                "explanation": "Compare standard deviations"
            }

        if concept == "skew":
            return {
                "q": f"If mean > median for {var}, distribution is?",
                "type": "mcq",
                "options": ["Positive skew","Negative skew"],
                "answer": "Positive skew",
                "explanation": "Mean > median → right skew"
            }

    # -----------------------------
    # NORMALITY
    # -----------------------------
    if topic == "Normality":

        return {
            "q": f"Shapiro test gives p=0.08. What do you conclude?",
            "type": "mcq",
            "options": ["Normal","Not normal"],
            "answer": "Normal",
            "explanation": "p > 0.05 → normal"
        }

    # -----------------------------
    # SUBSET ANALYSIS
    # -----------------------------
    if topic == "Subset Analysis":

        region = np.random.choice(df["Region"].unique())
        segment = np.random.choice(df["Segment"].unique())

        sub = df[(df["Region"]==region) & (df["Segment"]==segment)]

        return {
            "q": f"Compute mean Sales for Region={region}, Segment={segment}",
            "type": "numeric",
            "answer": sub["Sales"].mean(),
            "explanation": "Filtered subset mean"
        }

    # -----------------------------
    # PROBABILITY
    # -----------------------------
    if topic == "Probability":

        x = np.random.choice(df["Marketing"])
        mu = df["Marketing"].mean()
        sd = df["Marketing"].std()

        return {
            "q": f"Compute P(X < {round(x,2)}) assuming normal distribution",
            "type": "numeric",
            "answer": stats.norm.cdf(x, mu, sd),
            "explanation": "Use normal CDF"
        }

    # -----------------------------
    # HYPOTHESIS TESTING
    # -----------------------------
    if topic == "Hypothesis Testing":

        case = np.random.choice(["decision","test_select","pvalue"])

        if case == "decision":
            return {
                "q": "p-value = 0.03. What is decision?",
                "type": "mcq",
                "options": ["Reject null","Do not reject"],
                "answer": "Reject null",
                "explanation": "p < alpha → reject"
            }

        if case == "test_select":
            return {
                "q": "Data not normal. Which test for 2 independent samples?",
                "type": "mcq",
                "options": ["t-test","Mann-Whitney","ANOVA"],
                "answer": "Mann-Whitney",
                "explanation": "Non-parametric test"
            }

        if case == "pvalue":
            return {
                "q": "What does p-value represent?",
                "type": "text",
                "answer": "probability under null",
                "explanation": "Probability of observing data under null hypothesis"
            }

# -----------------------------
# GENERATE NEW QUESTION
# -----------------------------
if st.button("Next Question") or st.session_state.current_q is None:
    st.session_state.current_q = generate_question(topic, df)

q = st.session_state.current_q

st.subheader(q["q"])

# -----------------------------
# INPUT
# -----------------------------
if q["type"] == "numeric":
    user = st.number_input("Your Answer")

elif q["type"] == "mcq":
    user = st.radio("Choose", q["options"])

# -----------------------------
# SUBMIT
# -----------------------------
if st.button("Submit Answer"):

    st.session_state.total += 1

    correct = False

    if q["type"] == "numeric":
        correct = abs(user - q["answer"]) < 0.5

    else:
        correct = user == q["answer"]

    if correct:
        st.success("✅ Correct")
        st.session_state.score += 1
    else:
        st.error(f"""
❌ Incorrect  

Correct Answer ≈ {round(q['answer'],3)}  

📘 Explanation: {q['explanation']}  

⚠️ Likely mistake:
- Formula error
- Using wrong subset
- Concept confusion
""")

    st.write(f"Score: {st.session_state.score}/{st.session_state.total}")
