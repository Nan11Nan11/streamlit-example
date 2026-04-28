import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import random

st.set_page_config(page_title="AI Analytics Engine", layout="wide")

# =============================
# DATA GENERATION
# =============================
def generate_dataset(n=500):

    X1 = np.random.normal(600, 100, n)
    X2 = np.random.uniform(0, 2, n)
    X3 = np.random.normal(0.3, 0.05, n)
    X4 = np.random.normal(0.1, 0.05, n)
    X5 = np.random.normal(0.2, 0.07, n)

    X6 = np.random.choice(["Chem", "Eng"], n)
    X7 = np.random.choice(["High", "Low"], n)
    X8 = np.random.choice(["Y", "N"], n)

    Y = (
        50
        + 0.002 * X1
        + 2 * X3
        - 1.5 * X5
        + np.random.normal(0, 1, n)
    )

    return pd.DataFrame({
        "X1": X1,
        "X2": X2,
        "X3": X3,
        "X4": X4,
        "X5": X5,
        "X6": X6,
        "X7": X7,
        "X8": X8,
        "Y": Y
    })


# =============================
# VARIABLE MAPPING
# =============================
def generate_mapping():
    names = [
        "CreditScore", "Leverage", "Margin", "Growth",
        "CostRatio", "Sector", "MarketCap", "GlobalFlag", "Profit"
    ]
    random.shuffle(names)

    keys = ["X1","X2","X3","X4","X5","X6","X7","X8","Y"]

    return dict(zip(keys, names))


# =============================
# QUESTION ENGINE
# =============================
def generate_question(df):

    q_type = random.choice(["mean", "ttest", "regression"])

    # ---------------- MEAN ----------------
    if q_type == "mean":
        col = "X1"
        ans = df[col].mean()

        return {
            "type": "numeric",
            "question": f"What is the mean of {col}?",
            "answer": round(ans, 2),
            "explanation": f"Mean = {round(ans,2)}"
        }

    # ---------------- T-TEST ----------------
    elif q_type == "ttest":

        g1 = df[df["X8"]=="Y"]["X1"]
        g2 = df[df["X8"]=="N"]["X1"]

        t, p = stats.ttest_ind(g1, g2)

        # one-tailed randomly
        if random.choice([True, False]):
            p = p/2

        return {
            "type": "numeric",
            "question": "Enter p-value for difference in X1 across X8 groups",
            "answer": round(p, 4),
            "explanation": f"p-value = {round(p,4)}"
        }

    # ---------------- REGRESSION ----------------
    else:

        X = sm.add_constant(df[["X1","X3","X5"]])
        model = sm.OLS(df["Y"], X).fit()

        r2 = model.rsquared

        return {
            "type": "numeric",
            "question": "What is R-squared of regression?",
            "answer": round(r2, 3),
            "explanation": f"R² = {round(r2,3)}"
        }


# =============================
# SESSION INIT
# =============================
if "df" not in st.session_state:
    st.session_state.df = generate_dataset()
    st.session_state.map = generate_mapping()
    st.session_state.q = generate_question(st.session_state.df)
    st.session_state.answered = False

df = st.session_state.df
mapping = st.session_state.map
q = st.session_state.q

# =============================
# DISPLAY DATA
# =============================
df_display = df.rename(columns=mapping)

st.title("📊 AI Analytics Engine")

st.dataframe(df_display.head(15))

# =============================
# QUESTION
# =============================
st.subheader("Question")
question = q["question"]

for k,v in mapping.items():
    question = question.replace(k, v)

st.write(question)

user = st.number_input("Answer", format="%.4f")

# =============================
# SUBMIT
# =============================
if st.button("Submit"):

    if abs(user - q["answer"]) < 0.05:
        st.success("Correct")
    else:
        st.error("Incorrect")
        st.write("Correct:", q["answer"])

    st.write(q["explanation"])

# =============================
# NEXT
# =============================
if st.button("Next Question"):
    st.session_state.q = generate_question(df)
    st.rerun()

# =============================
# NEW SESSION
# =============================
if st.button("New Dataset"):
    st.session_state.df = generate_dataset()
    st.session_state.map = generate_mapping()
    st.session_state.q = generate_question(st.session_state.df)
    st.rerun()
