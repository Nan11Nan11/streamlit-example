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
for key, val in {
    "module":0,
    "qtype":0,
    "cleared":[],
    "prev_difficulty":None
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------
# MODULES
# -------------------------
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

# RESET ON DIFFICULTY CHANGE
if st.session_state.prev_difficulty != difficulty:
    st.session_state.module = 0
    st.session_state.qtype = 0
    st.session_state.cleared = []
    st.session_state.prev_difficulty = difficulty
    st.rerun()

# -------------------------
# COMPLETION CHECK
# -------------------------
if st.session_state.module >= len(modules):
    st.success("🎓 Congratulations! You have completed ALL modules.")
    st.stop()

st.subheader(f"Current Module: {modules[st.session_state.module]}")

# -------------------------
# QUESTION ENGINE
# -------------------------
def descriptive_question(qtype):

    var = np.random.choice(["Marketing","Cost","Satisfaction"])
    cat = np.random.choice(["Region","Segment"])

    # TYPE 1: variability comparison
    if qtype == 0:
        v1, v2 = np.random.choice(["Marketing","Cost","Satisfaction"],2,replace=False)

        return {
            "q": f"Compare variability: Which has higher dispersion ({v1} or {v2})?",
            "type":"mcq",
            "options":[v1,v2],
            "answer": v1 if df[v1].std()>df[v2].std() else v2,
            "explanation": f"""
Correct method: Compare standard deviations.

SD({v1}) = {round(df[v1].std(),2)}
SD({v2}) = {round(df[v2].std(),2)}

Higher SD ⇒ more variability.
"""
        }

    # TYPE 2: probability
    if qtype == 1:

        if difficulty == "Easy":
            x = df[var].mean()

            return {
                "q": f"Mean of {var} is {round(x,2)}. Compute P({var} < mean) assuming normal distribution.",
                "type":"numeric",
                "answer":0.5,
                "explanation":"In normal distribution, P(X < mean) = 0.5"
            }

        elif difficulty == "Medium":
            filt_value = df[cat].unique()[0]

return {
    "q": f"""
Using the dataset:

1. Filter observations where {cat} = {filt_value}  
2. Compute mean and standard deviation of {var}  
3. Assuming normal distribution, compute:

P({var} < mean)

Enter ONLY the final probability
""",
    "type":"numeric",
    "answer":0.5,
    "explanation": f"""
Step-by-step solution:

1. Filter dataset where {cat} = {filt_value}

2. Compute:
   Mean (μ) and Standard Deviation (σ) of {var}

3. Since we are computing:
   P(X < mean)

For ANY normal distribution:
   P(X < μ) = 0.5

Key learning:
Even after filtering, the theoretical probability at mean is always 0.5.
"""
}
                
            }

        else:  # HARD
            x = float(np.random.choice(df[var]))
            mu, sd = df[var].mean(), df[var].std()

            return {
                "q": f"""
Variable: {var}

Mean = {round(mu,2)}, SD = {round(sd,2)}

Compute:
1. Theoretical P({var} < {round(x,2)})
2. Observed P({var} < {round(x,2)})

Enter ONLY theoretical value
""",
                "type":"numeric",
                "answer": stats.norm.cdf(x,mu,sd),
                "explanation": f"""
Theoretical uses normal distribution.

Observed would be:
count(values < X) / total

Difference occurs if data not perfectly normal.
"""
            }

    # TYPE 3: interpretation
    if qtype == 2:
        skew = stats.skew(df[var])
        kurt = stats.kurtosis(df[var])

        return {
            "q": f"""
Variable {var} has:

Skewness = {round(skew,2)}
Kurtosis = {round(kurt,2)}

Interpret distribution
""",
            "type":"text",
            "answer":"",
            "explanation": f"""
Skew > 0 ⇒ right skew  
Kurtosis:
>0 ⇒ heavy tails  
<0 ⇒ light tails
"""
        }


def hypothesis_question(qtype):

    if qtype == 0:
        return {
            "q":"Data is NOT normal. Which test for 2 independent samples?",
            "type":"mcq",
            "options":["t-test","Mann-Whitney","ANOVA"],
            "answer":"Mann-Whitney",
            "explanation":"Non-parametric test for independent samples"
        }

    if qtype == 1:
        return {
            "q":"p-value = 0.03. Decision?",
            "type":"mcq",
            "options":["Reject null","Do not reject"],
            "answer":"Reject null",
            "explanation":"p < 0.05 ⇒ reject H0"
        }

    if qtype == 2:
        return {
            "q":"Data normal but variances unequal. Which test?",
            "type":"mcq",
            "options":["Student t","Welch t","Chi-square"],
            "answer":"Welch t",
            "explanation":"Welch handles unequal variance"
        }


def anova_question(qtype):

    if qtype == 0:
        return {
            "q":"Non-normal data, 3 groups. Which test?",
            "type":"mcq",
            "options":["ANOVA","Kruskal-Wallis","t-test"],
            "answer":"Kruskal-Wallis",
            "explanation":"Non-parametric ANOVA"
        }

    if qtype == 1:
        return {
            "q":"Normal + unequal variance. Which ANOVA?",
            "type":"mcq",
            "options":["Fisher","Welch","Chi-square"],
            "answer":"Welch",
            "explanation":"Welch ANOVA"
        }

    if qtype == 2:
        return {
            "q":"Post-hoc for unequal variance?",
            "type":"mcq",
            "options":["Tukey","Games-Howell","DSCF"],
            "answer":"Games-Howell",
            "explanation":"Used when variance unequal"
        }


def regression_question(qtype):

    if qtype == 0:
        return {
            "q":"Which test detects heteroskedasticity?",
            "type":"mcq",
            "options":["Durbin Watson","Breusch Pagan","VIF"],
            "answer":"Breusch Pagan",
            "explanation":"Variance of residuals"
        }

    if qtype == 1:
        return {
            "q":"High VIF indicates?",
            "type":"mcq",
            "options":["Normality","Multicollinearity","Autocorrelation"],
            "answer":"Multicollinearity",
            "explanation":"Predictors correlated"
        }

    if qtype == 2:
        return {
            "q":"Durbin Watson checks?",
            "type":"mcq",
            "options":["Variance","Autocorrelation","Mean"],
            "answer":"Autocorrelation",
            "explanation":"Residual correlation"
        }


# -------------------------
# SELECT QUESTION
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

question_key = f"{st.session_state.module}_{st.session_state.qtype}"

if q["type"] == "mcq":
    ans = st.radio("", q["options"], key=f"mcq_{question_key}")

elif q["type"] == "numeric":
    ans = st.number_input("Answer", key=f"num_{question_key}")

else:
    ans = st.text_area("Answer", key=f"text_{question_key}")

# -------------------------
# EVALUATE
# -------------------------
if st.button("Submit"):

    if q["type"] == "numeric":
        correct = abs(ans - q["answer"]) < 0.5
    elif q["type"] == "mcq":
        correct = ans == q["answer"]
    else:
        correct = len(ans.strip()) > 10

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

👉 Try a similar question again.
""")
