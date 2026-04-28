import streamlit as st
import numpy as np
import random

st.set_page_config(layout="wide")

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
# HYPOTHESIS ENGINE (YOUR PEDAGOGY)
# -------------------------
def hypothesis_engine(difficulty):

    scenario = random.choice(["one_sample", "two_sample"])

    # -------------------
    # ONE SAMPLE
    # -------------------
    if scenario == "one_sample":

        qtype = random.choice([
            "test_choice",
            "normality",
            "interpretation"
        ])

        if qtype == "test_choice":
            return {
                "q": "You have a sample of body temperature and want to check if it is significantly higher than 98. Which test should you use?",
                "type": "mcq",
                "options": ["One sample t-test", "Independent t-test", "ANOVA"],
                "answer": "One sample t-test",
                "explanation": "One sample compared to a fixed value → One sample t-test"
            }

        if qtype == "normality":
            return {
                "q": "Shapiro-Wilk p-value = 0.23. What does this indicate?",
                "type": "mcq",
                "options": ["Data is normal", "Data is not normal"],
                "answer": "Data is normal",
                "explanation": "p > 0.05 ⇒ data is approximately normal"
            }

        if qtype == "interpretation":
            return {
                "q": "The p-value of a one sample t-test is 0.03. What is your conclusion?",
                "type": "mcq",
                "options": ["Reject null hypothesis", "Do not reject null"],
                "answer": "Reject null hypothesis",
                "explanation": "p < 0.05 ⇒ statistically significant ⇒ reject null"
            }

    # -------------------
    # TWO SAMPLE
    # -------------------
    else:

        qtype = random.choice([
            "test_identification",
            "normality_fail",
            "variance_case",
            "full_decision"
        ])

        if qtype == "test_identification":
            return {
                "q": "You compare body temperature of people with heart rate > 75 vs ≤ 75. Which test is appropriate?",
                "type": "mcq",
                "options": ["Independent t-test", "One sample test", "Chi-square"],
                "answer": "Independent t-test",
                "explanation": "Two independent groups → Independent samples test"
            }

        if qtype == "normality_fail":
            return {
                "q": "Shapiro-Wilk p-value = 0.01. Which test should you use?",
                "type": "mcq",
                "options": ["Student t-test", "Mann-Whitney"],
                "answer": "Mann-Whitney",
                "explanation": "p < 0.05 ⇒ non-normal ⇒ use non-parametric test"
            }

        if qtype == "variance_case":
            return {
                "q": "Data is normal but Levene test p-value = 0.02. Which test is appropriate?",
                "type": "mcq",
                "options": ["Student t-test", "Welch t-test"],
                "answer": "Welch t-test",
                "explanation": "Unequal variances ⇒ Welch test"
            }

        if qtype == "full_decision":
            return {
                "q": "Data is normal and Levene p-value = 0.40. Which test should be used?",
                "type": "mcq",
                "options": ["Student t-test", "Welch t-test"],
                "answer": "Student t-test",
                "explanation": "Normal + equal variance ⇒ Student t-test"
            }

# -------------------------
# DESCRIPTIVE ENGINE (SIMPLE FOR NOW)
# -------------------------
def descriptive_engine():

    qtype = random.choice(["variability", "skew"])

    if qtype == "variability":
        return {
            "q": "Which measure is used to compare variability?",
            "type": "mcq",
            "options": ["Mean", "Standard deviation", "Median"],
            "answer": "Standard deviation",
            "explanation": "Standard deviation measures dispersion"
        }

    else:
        return {
            "q": "If skewness is positive, what does it indicate?",
            "type": "mcq",
            "options": ["Left skew", "Right skew"],
            "answer": "Right skew",
            "explanation": "Positive skew ⇒ right tail"
        }

# -------------------------
# ANOVA ENGINE
# -------------------------
def anova_engine():

    qtype = random.choice(["selection", "variance", "posthoc"])

    if qtype == "selection":
        return {
            "q": "Data is non-normal across 3 groups. Which test should you use?",
            "type": "mcq",
            "options": ["ANOVA", "Kruskal-Wallis"],
            "answer": "Kruskal-Wallis",
            "explanation": "Non-normal ⇒ non-parametric ANOVA"
        }

    if qtype == "variance":
        return {
            "q": "Data is normal but variances are unequal. Which ANOVA variant?",
            "type": "mcq",
            "options": ["Fisher ANOVA", "Welch ANOVA"],
            "answer": "Welch ANOVA",
            "explanation": "Unequal variance ⇒ Welch ANOVA"
        }

    return {
        "q": "Post-hoc test for unequal variance?",
        "type": "mcq",
        "options": ["Tukey", "Games-Howell"],
        "answer": "Games-Howell",
        "explanation": "Used when variances are unequal"
    }

# -------------------------
# REGRESSION ENGINE
# -------------------------
def regression_engine():

    qtype = random.choice(["hetero", "vif", "dw"])

    if qtype == "hetero":
        return {
            "q": "Which test detects heteroskedasticity?",
            "type": "mcq",
            "options": ["Durbin Watson", "Breusch Pagan", "VIF"],
            "answer": "Breusch Pagan",
            "explanation": "Breusch-Pagan checks variance of residuals"
        }

    if qtype == "vif":
        return {
            "q": "High VIF indicates:",
            "type": "mcq",
            "options": ["Normality", "Multicollinearity"],
            "answer": "Multicollinearity",
            "explanation": "High VIF ⇒ predictors are correlated"
        }

    return {
        "q": "Durbin Watson test checks:",
        "type": "mcq",
        "options": ["Autocorrelation", "Variance"],
        "answer": "Autocorrelation",
        "explanation": "Durbin Watson detects serial correlation"
    }

# -------------------------
# QUESTION ROUTER
# -------------------------
def get_question(difficulty):

    module = modules[st.session_state.module]

    if module == "Descriptive Stats":
        return descriptive_engine()

    elif module == "Hypothesis Testing":
        return hypothesis_engine(difficulty)

    elif module == "ANOVA":
        return anova_engine()

    else:
        return regression_engine()

# -------------------------
# UI
# -------------------------
st.title("📊 Business Analytics Learning System")

difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])

st.subheader(f"Module: {modules[st.session_state.module]}")

# Generate question
if st.session_state.question is None or st.session_state.correct:
    st.session_state.question = get_question(difficulty)
    st.session_state.correct = False

q = st.session_state.question

st.write(q["q"])

user_ans = st.radio("Select answer:", q["options"])

# -------------------------
# EVALUATION
# -------------------------
if st.button("Submit"):

    if user_ans == q["answer"]:
        st.success("✅ Correct!")

        st.session_state.correct = True
        st.session_state.question = None

        # Move module after few correct answers
        if random.random() > 0.6:
            st.session_state.module += 1

            if st.session_state.module >= len(modules):
                st.success("🎓 You completed all modules!")
                st.stop()

    else:
        st.error("❌ Incorrect")

        st.write("### Explanation:")
        st.write(q["explanation"])

        # Repeat similar concept
        st.session_state.correct = False
