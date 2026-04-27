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
def generate_question(topic, df):

    if topic == "Descriptive":
        var = np.random.choice(["Marketing","Cost","Satisfaction"])
        return {
            "q": f"Compute mean of {var}",
            "type": "numeric",
            "answer": df[var].mean(),
            "explanation": f"Mean = average of {var}"
        }

    if topic == "Normality":
        return {
            "q": "If p-value > 0.05 in Shapiro test, data is?",
            "type": "mcq",
            "options": ["Normal","Not normal"],
            "answer": "Normal",
            "explanation": "p > 0.05 → fail to reject normality"
        }

    if topic == "Subset Analysis":
        region = np.random.choice(df["Region"].unique())
        sub = df[df["Region"] == region]

        return {
            "q": f"Compute mean Sales for Region = {region}",
            "type": "numeric",
            "answer": sub["Sales"].mean(),
            "explanation": "Filtered mean calculation"
        }

    if topic == "Probability":
        x = np.random.choice(df["Marketing"])
        mu = df["Marketing"].mean()
        sd = df["Marketing"].std()

        prob = stats.norm.cdf(x, mu, sd)

        return {
            "q": f"Approx probability P(X < {round(x,2)}) for Marketing",
            "type": "numeric",
            "answer": prob,
            "explanation": "Using normal distribution CDF"
        }

    if topic == "Hypothesis Testing":

        sample = df["Marketing"].sample(40)
        mean = sample.mean()
        sd = sample.std()
        n = len(sample)

        t_val = (mean - 50)/(sd/np.sqrt(n))

        return {
            "q": f"Compute t-stat (mean={round(mean,2)}, sd={round(sd,2)}, n={n})",
            "type": "numeric",
            "answer": t_val,
            "explanation": "t = (mean - hypo)/SE"
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
