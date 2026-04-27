import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(layout="wide")

# -------------------------
# DATASET
# -------------------------
if "df" not in st.session_state:
    np.random.seed(42)

    df = pd.DataFrame({
        "Marketing": np.random.normal(50,10,120),
        "Cost": np.random.normal(40,12,120),
        "Satisfaction": np.random.normal(70,8,120),
        "Productivity": np.random.normal(60,15,120),
        "Market_Share": np.random.normal(30,5,120),
        "Region": np.random.choice(["North","South","East","West"],120),
        "Segment": np.random.choice(["Retail","Corporate"],120),
        "Strategy": np.random.choice(["Aggressive","Conservative"],120)
    })

    df["Sales"] = 0.5*df["Marketing"] + 0.3*df["Satisfaction"] - 0.2*df["Cost"] + np.random.normal(0,5,120)

    st.session_state.df = df

df = st.session_state.df

# -------------------------
# INIT STATE
# -------------------------
if "module" not in st.session_state:
    st.session_state.module = 0
if "qtype" not in st.session_state:
    st.session_state.qtype = 0
if "prev_difficulty" not in st.session_state:
    st.session_state.prev_difficulty = None

modules = [
    "Descriptive Stats",
    "Hypothesis Testing",
    "ANOVA",
    "Linear Regression"
]

# -------------------------
# HEADER
# -------------------------
st.title("📊 Business Analytics Learning System")

name = st.text_input("Student Name")

difficulty = st.selectbox("Select Difficulty", ["Easy","Medium","Hard"])

# RESET when difficulty changes
if st.session_state.prev_difficulty != difficulty:
    st.session_state.module = 0
    st.session_state.qtype = 0
    st.session_state.prev_difficulty = difficulty
    st.rerun()

# -------------------------
# END CONDITION
# -------------------------
if st.session_state.module >= len(modules):
    st.success("🎓 Congratulations! You have completed ALL modules.")
    st.stop()

st.subheader(f"Current Module: {modules[st.session_state.module]}")

# -------------------------
# DESCRIPTIVE QUESTIONS
# -------------------------
def descriptive_question(qtype):

    var = np.random.choice(["Marketing","Cost","Satisfaction"])
    cat = np.random.choice(["Region","Segment"])

    # Q1: variability
    if qtype == 0:
        v1, v2 = np.random.choice(["Marketing","Cost","Satisfaction"],2,replace=False)

        return {
            "q": f"Which variable has higher variability: {v1} or {v2}?",
            "type":"mcq",
            "options":[v1,v2],
            "answer": v1 if df[v1].std()>df[v2].std() else v2,
            "explanation": f"""
Compare standard deviations:

SD({v1}) = {round(df[v1].std(),2)}
SD({v2}) = {round(df[v2].std(),2)}

Higher SD ⇒ more variability.
"""
        }

    # Q2: probability
    if qtype == 1:

        if difficulty == "Easy":
            return {
                "q": f"For variable {var}, compute P(X < mean) assuming normal distribution.",
                "type":"numeric",
                "answer":0.5,
                "explanation":"For any normal distribution: P(X < mean) = 0.5"
            }

        elif difficulty == "Medium":
            filt = df[cat].unique()[0]

    return {
        "q": f"""
Using the dataset:

1. Filter rows where {cat} = {filt}
2. Compute mean (μ) and standard deviation (σ) of {var}
3. Compute:

P({var} < μ) assuming normal distribution

Enter final probability
""",
        "type":"numeric",
        "answer":0.5,
        "explanation":"""
Even after filtering, for ANY normal distribution:

P(X < mean) = 0.5

Key insight:
Student must compute mean first → then apply concept.
"""
    }

else:  # HARD
    filt = df[cat].unique()[0]
    x = float(np.random.choice(df[var]))

    return {
        "q": f"""
Using the dataset:

1. Filter rows where {cat} = {filt}
2. Compute mean (μ) and standard deviation (σ) of {var}
3. Compute:

P({var} < {round(x,2)}) assuming normal distribution

Enter final probability
""",
        "type":"numeric",
        "answer": stats.norm.cdf(x, df[var].mean(), df[var].std()),
        "explanation": f"""
Steps:

1. Filter dataset
2. Compute μ and σ manually
3. Standardize:

Z = (X - μ) / σ

4. Use normal table / CDF

This tests:
✔ Data handling  
✔ Parameter estimation  
✔ Probability computation  
"""
    }

# -------------------------
# OTHER MODULES (CLEAN)
# -------------------------
def hypothesis_question(qtype):

    questions = [
        ("Non-normal data, 2 independent samples?", ["t-test","Mann-Whitney","ANOVA"], "Mann-Whitney"),
        ("p-value = 0.03 → decision?", ["Reject","Do not reject"], "Reject"),
        ("Normal but unequal variance?", ["Student t","Welch t"], "Welch t")
    ]

    q = questions[qtype]

    return {
        "q": q[0],
        "type":"mcq",
        "options": q[1],
        "answer": q[2],
        "explanation":"Based on statistical test selection rules"
    }

def anova_question(qtype):

    questions = [
        ("Non-normal, 3 groups?", ["ANOVA","Kruskal"], "Kruskal"),
        ("Normal unequal variance?", ["Fisher","Welch"], "Welch"),
        ("Post-hoc unequal variance?", ["Tukey","Games-Howell"], "Games-Howell")
    ]

    q = questions[qtype]

    return {
        "q": q[0],
        "type":"mcq",
        "options": q[1],
        "answer": q[2],
        "explanation":"ANOVA decision logic"
    }

def regression_question(qtype):

    questions = [
        ("Detect heteroskedasticity?", ["Durbin","Breusch Pagan","VIF"], "Breusch Pagan"),
        ("High VIF means?", ["Normality","Multicollinearity"], "Multicollinearity"),
        ("Durbin Watson checks?", ["Variance","Autocorrelation"], "Autocorrelation")
    ]

    q = questions[qtype]

    return {
        "q": q[0],
        "type":"mcq",
        "options": q[1],
        "answer": q[2],
        "explanation":"Regression diagnostics"
    }

# -------------------------
# QUESTION SELECT
# -------------------------
if st.session_state.module == 0:
    q = descriptive_question(st.session_state.qtype)
elif st.session_state.module == 1:
    q = hypothesis_question(st.session_state.qtype)
elif st.session_state.module == 2:
    q = anova_question(st.session_state.qtype)
else:
    q = regression_question(st.session_state.qtype)

# -------------------------
# DISPLAY
# -------------------------
st.write(q["q"])

if q["type"] == "mcq":
    ans = st.radio("", q["options"])
elif q["type"] == "numeric":
    ans = st.number_input("Answer")
else:
    ans = st.text_area("Answer")

# -------------------------
# EVALUATION
# -------------------------
if st.button("Submit"):

    if q["type"] == "numeric":
        correct = abs(ans - q["answer"]) < 0.05
    elif q["type"] == "mcq":
        correct = ans == q["answer"]
    else:
        correct = len(ans.strip()) > 15

    if correct:
        st.success("✅ Correct")

        st.session_state.qtype += 1

        if st.session_state.qtype > 2:
            st.success("🎉 Module Cleared")
            st.session_state.module += 1
            st.session_state.qtype = 0

        st.rerun()

    else:
        st.error(f"""
❌ Incorrect

Correct Answer: {q['answer']}

Explanation:
{q['explanation']}

👉 Try again
""")
