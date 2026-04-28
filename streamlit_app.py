import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

st.set_page_config(page_title="Business Analytics Learning System")

# -----------------------------
# DATA GENERATION
# -----------------------------
def generate_dataset(n=60):
    heart_rate = np.random.randint(55, 95, n)
    gender = np.random.choice(["Male", "Female"], n)
    body_temp = 97 + 0.03 * heart_rate + np.random.normal(0, 0.5, n)

    df = pd.DataFrame({
        "HeartRate": heart_rate,
        "BodyTemp": body_temp,
        "Gender": gender
    })

    df["HT_GT_75"] = (df["HeartRate"] > 75).astype(int)
    return df

# -----------------------------
# JAMOVI ENGINES
# -----------------------------
def run_ttest(df):
    g1 = df[df["HeartRate"] > 75]["BodyTemp"]
    g2 = df[df["HeartRate"] <= 75]["BodyTemp"]

    p1 = stats.shapiro(g1)[1]
    p2 = stats.shapiro(g2)[1]
    lev = stats.levene(g1, g2)[1]

    if p1 > 0.05 and p2 > 0.05:
        if lev > 0.05:
            test = "Student t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=True)
        else:
            test = "Welch t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=False)
    else:
        test = "Mann-Whitney U"
        stat, pval = stats.mannwhitneyu(g1, g2)

    decision = "Reject H0" if pval < 0.05 else "Fail to Reject H0"

    return {
        "test": test,
        "pval": pval,
        "decision": decision,
        "normality": (p1, p2),
        "levene": lev
    }

def run_regression(df):
    X = sm.add_constant(df["HeartRate"])
    y = df["BodyTemp"]
    model = sm.OLS(y, X).fit()

    return {
        "slope": model.params["HeartRate"],
        "pval": model.pvalues["HeartRate"],
        "r2": model.rsquared
    }

# -----------------------------
# JAMOVI OUTPUT UI
# -----------------------------
def show_ttest_output(res):
    st.markdown("### 📊 Jamovi Output (Simplified)")
    st.code(f"""
Test: {res['test']}
p-value: {round(res['pval'],4)}
Normality p-values: {round(res['normality'][0],4)}, {round(res['normality'][1],4)}
Levene p-value: {round(res['levene'],4)}
Decision: {res['decision']}
""")

def show_regression_output(res):
    st.markdown("### 📊 Jamovi Output (Simplified)")
    st.code(f"""
Model: BodyTemp ~ HeartRate
Slope: {round(res['slope'],3)}
p-value: {round(res['pval'],4)}
R²: {round(res['r2'],3)}
""")

# -----------------------------
# QUESTION GENERATOR (WITH DIFFICULTY)
# -----------------------------
def generate_question(df, difficulty):

    module = np.random.choice(["descriptive", "hypothesis", "regression"])

    # ---------------- EASY ----------------
    if difficulty == "Easy":

        col = np.random.choice(["HeartRate", "BodyTemp"])
        mean_val = df[col].mean()

        return {
            "type": "numeric",
            "question": f"What is the mean of {col}?",
            "answer": round(mean_val, 2),
            "explanation": f"Mean = {round(mean_val,2)}",
            "jamovi": None
        }

    # ---------------- MEDIUM ----------------
    elif difficulty == "Medium":

        if module == "hypothesis":
            res = run_ttest(df)

            return {
                "type": "numeric",
                "question": "Enter the p-value from the test",
                "answer": round(res["pval"], 4),
                "explanation": f"p-value = {round(res['pval'],4)}",
                "jamovi": ("ttest", res)
            }

        else:
            res = run_regression(df)

            return {
                "type": "numeric",
                "question": "What is the slope of regression?",
                "answer": round(res["slope"], 3),
                "explanation": f"Slope = {round(res['slope'],3)}",
                "jamovi": ("regression", res)
            }

    # ---------------- HARD ----------------
    else:

        if module == "hypothesis":
            res = run_ttest(df)

            return {
                "type": "mcq",
                "question": "What is the correct conclusion?",
                "options": [
                    "Reject H0",
                    "Fail to Reject H0"
                ],
                "answer": res["decision"],
                "explanation": f"Decision based on p-value = {round(res['pval'],4)}",
                "jamovi": ("ttest", res)
            }

        else:
            res = run_regression(df)

            return {
                "type": "mcq",
                "question": "Is HeartRate a significant predictor?",
                "options": [
                    "Yes",
                    "No"
                ],
                "answer": "Yes" if res["pval"] < 0.05 else "No",
                "explanation": f"p-value = {round(res['pval'],4)}",
                "jamovi": ("regression", res)
            }

# -----------------------------
# SESSION STATE
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = generate_dataset()
    st.session_state.q = None
    st.session_state.answered = False
    st.session_state.correct = None

# -----------------------------
# UI
# -----------------------------
st.title("📊 Business Analytics Learning System")

difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])

# -----------------------------
# NEW SESSION
# -----------------------------
if st.button("🔄 Start New Session"):
    st.session_state.df = generate_dataset()
    st.session_state.q = None
    st.session_state.answered = False
    st.session_state.correct = None
    st.rerun()

# -----------------------------
# SHOW DATA
# -----------------------------
st.subheader("Dataset")
st.dataframe(st.session_state.df.head(15))

# -----------------------------
# GENERATE QUESTION ONCE
# -----------------------------
if st.session_state.q is None:
    st.session_state.q = generate_question(st.session_state.df, difficulty)

q = st.session_state.q

# -----------------------------
# SHOW JAMOVI OUTPUT (IF ANY)
# -----------------------------
if q["jamovi"] is not None:
    kind, res = q["jamovi"]

    if kind == "ttest":
        show_ttest_output(res)
    else:
        show_regression_output(res)

# -----------------------------
# QUESTION
# -----------------------------
st.subheader("Current Question")
st.write(q["question"])

# -----------------------------
# INPUT
# -----------------------------
if q["type"] == "numeric":
    user_ans = st.number_input("Enter answer", value=0.0, step=0.01)
else:
    user_ans = st.radio("Select answer", q["options"])

# -----------------------------
# SUBMIT
# -----------------------------
if st.button("Submit") and not st.session_state.answered:

    if q["type"] == "numeric":
        correct = abs(user_ans - q["answer"]) <= 0.02
    else:
        correct = user_ans == q["answer"]

    st.session_state.correct = correct
    st.session_state.answered = True

# -----------------------------
# RESULT
# -----------------------------
if st.session_state.answered:

    if st.session_state.correct:
        st.success("Correct ✅")
    else:
        st.error("Incorrect ❌")

    st.write(f"Your answer: {user_ans}")

    if q["type"] == "numeric":
        st.write(f"Accepted range: {round(q['answer']-0.02,3)} to {round(q['answer']+0.02,3)}")
    else:
        st.write(f"Correct answer: {q['answer']}")

    st.markdown("### 🔍 Explanation")
    st.write(q["explanation"])

    # -----------------------------
    # NEXT QUESTION
    # -----------------------------
    if st.button("Next Question"):
        st.session_state.q = generate_question(st.session_state.df, difficulty)
        st.session_state.answered = False
        st.session_state.correct = None
        st.rerun()
