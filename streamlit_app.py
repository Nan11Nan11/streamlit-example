import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(layout="wide")

# -------------------------
# INIT
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

if "module" not in st.session_state:
    st.session_state.module = 0

if "qtype" not in st.session_state:
    st.session_state.qtype = 0

if "cleared" not in st.session_state:
    st.session_state.cleared = []

df = st.session_state.df

# -------------------------
# MODULES
# -------------------------
modules = [
    "Descriptive Stats",
    "Hypothesis Testing",
    "ANOVA",
    "Linear Regression"
]

st.title("📊 Business Analytics Learning System")

name = st.text_input("Student Name")

difficulty = st.selectbox("Select Difficulty", ["Easy","Medium","Hard"])

if st.session_state.module < len(modules):
    st.write(f"### Current Module: {modules[st.session_state.module]}")
else:
    st.success("🎓 Congratulations! You have completed ALL modules.")
    st.stop()

# -------------------------
# QUESTION ENGINE
# -------------------------
def get_question(module, qtype):

    # -------------------------
    # DESCRIPTIVE
    # -------------------------
    if module == 0:

        # TYPE 1: variability comparison
        if qtype == 0:
            v1, v2 = np.random.choice(["Marketing","Cost","Satisfaction"],2,replace=False)

            return {
                "q": f"Which variable has higher variability: {v1} or {v2}?",
                "type":"mcq",
                "options":[v1,v2],
                "answer": v1 if df[v1].std()>df[v2].std() else v2,
                "explanation":"Compare standard deviations"
            }

        # TYPE 2: probability
        if qtype == 1:

            var = np.random.choice(["Marketing","Cost","Satisfaction"])
            x = float(np.random.choice(df[var]))
        
            mu = df[var].mean()
            sd = df[var].std()
        
            # randomly choose type of probability
            prob_type = np.random.choice(["theoretical","observed"])
        
            if prob_type == "theoretical":
                return {
                    "q": f"""
        For variable {var}:
        
        Mean (μ) = {round(mu,2)}  
        Standard Deviation (σ) = {round(sd,2)}  
        
        Assuming NORMAL distribution, compute:  
        P({var} < {round(x,2)})
        """,
                    "type":"numeric",
                    "answer": stats.norm.cdf(x, mu, sd),
                    "explanation": f"""
        This is a THEORETICAL probability.
        
        We assume normal distribution and compute:
        Z = (X - μ) / σ
        
        Then use standard normal CDF.
        """
                }
        
            else:
                observed_prob = (df[var] < x).mean()
        
                return {
                    "q": f"""
    For variable {var}:
    
    Using ACTUAL DATA (not normal assumption), compute:  
    P({var} < {round(x,2)})
    """,
                "type":"numeric",
                "answer": observed_prob,
                "explanation": f"""
    This is an OBSERVED probability.
    
    We count proportion of values less than {round(x,2)}:
    P = (Number of observations < X) / Total observations
    """
            }

        # TYPE 3: normality + skew
        if qtype == 2:
            return {
                "q":"If skewness > 0 and kurtosis > 3, interpret distribution",
                "type":"text",
                "answer":"right skew heavy tail",
                "explanation":"Positive skew and leptokurtic distribution"
            }

    # -------------------------
    # HYPOTHESIS
    # -------------------------
    if module == 1:

        if qtype == 0:
            return {
                "q":"Data not normal. Which test for 2 independent samples?",
                "type":"mcq",
                "options":["t-test","Mann-Whitney","ANOVA"],
                "answer":"Mann-Whitney",
                "explanation":"Non-parametric test"
            }

        if qtype == 1:
            return {
                "q":"p-value = 0.04. Decision?",
                "type":"mcq",
                "options":["Reject null","Do not reject"],
                "answer":"Reject null",
                "explanation":"p < 0.05"
            }

        if qtype == 2:
            return {
                "q":"Variances unequal, normal data. Which test?",
                "type":"mcq",
                "options":["Student t","Welch t","Chi-square"],
                "answer":"Welch t",
                "explanation":"Handles unequal variance"
            }

    # -------------------------
    # ANOVA
    # -------------------------
    if module == 2:

        if qtype == 0:
            return {
                "q":"Data normal, unequal variances. Which ANOVA?",
                "type":"mcq",
                "options":["Fisher","Welch","Kruskal"],
                "answer":"Welch",
                "explanation":"Welch ANOVA"
            }

        if qtype == 1:
            return {
                "q":"Which post-hoc for unequal variance?",
                "type":"mcq",
                "options":["Tukey","Games-Howell","DSCF"],
                "answer":"Games-Howell",
                "explanation":"Unequal variance case"
            }

        if qtype == 2:
            return {
                "q":"Non-normal ANOVA alternative?",
                "type":"mcq",
                "options":["Kruskal-Wallis","t-test","Z-test"],
                "answer":"Kruskal-Wallis",
                "explanation":"Non-parametric ANOVA"
            }

    # -------------------------
    # REGRESSION
    # -------------------------
    if module == 3:

        if qtype == 0:
            return {
                "q":"Test for heteroskedasticity?",
                "type":"mcq",
                "options":["Durbin Watson","Breusch Pagan","VIF"],
                "answer":"Breusch Pagan",
                "explanation":"Checks variance of errors"
            }

        if qtype == 1:
            return {
                "q":"Test for autocorrelation?",
                "type":"mcq",
                "options":["Durbin Watson","VIF","Shapiro"],
                "answer":"Durbin Watson",
                "explanation":"Time series residual correlation"
            }

        if qtype == 2:
            return {
                "q":"High VIF indicates?",
                "type":"mcq",
                "options":["Heteroskedasticity","Multicollinearity","Normality"],
                "answer":"Multicollinearity",
                "explanation":"Collinearity issue"
            }


# -------------------------
# ASK QUESTION
# -------------------------
q = get_question(st.session_state.module, st.session_state.qtype)

st.subheader(q["q"])

if q["type"] == "mcq":
    ans = st.radio("", q["options"])

elif q["type"] == "numeric":
    ans = st.number_input("Answer")

else:
    ans = st.text_area("Answer")

# -------------------------
# SUBMIT
# -------------------------
if st.button("Submit"):

    correct = False

    if q["type"] == "numeric":
        correct = abs(ans - q["answer"]) < 0.5

    elif q["type"] == "mcq":
        correct = ans == q["answer"]

    else:
        correct = len(ans) > 10

    if correct:
        st.success("Correct")
    
        st.session_state.qtype += 1
    
        if st.session_state.qtype > 2:
    
            st.success("🎉 MODULE CLEARED")
    
            st.session_state.cleared.append(modules[st.session_state.module])
    
            st.write(f"Certificate: {name} cleared {modules[st.session_state.module]} at {difficulty} level")
    
            if st.session_state.module < len(modules) - 1:
                st.session_state.module += 1
                st.session_state.qtype = 0
            else:
                st.session_state.module += 1  # allow completion state
    
        st.rerun()   # 🔥 ADD THIS LINE

    else:
        st.error(f"""
Incorrect  

Correct: {q['answer']}  

Explanation: {q['explanation']}  
Try similar question again
""")
