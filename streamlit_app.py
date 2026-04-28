import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = generate_dataset()

if "q" not in st.session_state:
    st.session_state.q = None

if "answered" not in st.session_state:
    st.session_state.answered = False

if "correct" not in st.session_state:
    st.session_state.correct = None
st.set_page_config(page_title="Business Analytics Learning System")

# -----------------------------
# DATA GENERATION
# -----------------------------
import numpy as np
import pandas as pd

def generate_dataset(n=120):

    np.random.seed()

    # -----------------------------
    # NUMERIC VARIABLES
    # -----------------------------
    heart_rate = np.random.normal(72, 8, n)
    age = np.random.randint(18, 65, n)
    income = np.random.normal(50000, 15000, n)
    stress = np.random.normal(5, 2, n)

    # -----------------------------
    # CATEGORICAL VARIABLES
    # -----------------------------
    gender = np.random.choice(["Male", "Female"], n)
    exercise = np.random.choice(["Low", "Medium", "High"], n, p=[0.3, 0.5, 0.2])
    smoker = np.random.choice(["Yes", "No"], n, p=[0.3, 0.7])

    # -----------------------------
    # DEPENDENT VARIABLE (BodyTemp)
    # Structured relationship (important)
    # -----------------------------
    body_temp = (
        97
        + 0.03 * heart_rate
        + 0.01 * stress
        - 0.002 * age
        + np.random.normal(0, 0.3, n)
    )

    df = pd.DataFrame({
        "HeartRate": heart_rate.round(0),
        "BodyTemp": body_temp.round(2),
        "Age": age,
        "Income": income.round(0),
        "StressScore": stress.round(1),
        "Gender": gender,
        "ExerciseLevel": exercise,
        "Smoker": smoker
    })

    return df
# -----------------------------
# SHOW DATASET (VISIBLE SAMPLE)
# -----------------------------
st.subheader("📊 Dataset (Preview)")
st.dataframe(st.session_state.df.head(15))
df = st.session_state.df
st.markdown("""
### 📘 Context

This dataset represents health and lifestyle indicators of individuals.

- HeartRate: beats per minute  
- BodyTemp: body temperature (°F)  
- Age: years  
- Income: annual income  
- StressScore: scale 1–10  
- ExerciseLevel: Low / Medium / High  
- Smoker: Yes / No  

👉 You will analyze this dataset using statistical tools.
""")

# -----------------------------
# DOWNLOAD FULL DATASET
# -----------------------------
csv = st.session_state.df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇️ Download Full Dataset (CSV)",
    data=csv,
    file_name=f"{st.session_state.student_name}_dataset.csv",
    mime="text/csv"
)
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

if st.button("🔄 Start New Session"):
    st.session_state.df = generate_dataset()
    st.session_state.question = None
    st.session_state.answered = False
    st.session_state.correct = None
    st.rerun()

# -----------------------------
# UI
# -----------------------------
st.title("📊 Business Analytics Learning System")

difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
# -----------------------------
# SHOW DATA
# -----------------------------
st.subheader("Dataset")
st.dataframe(st.session_state.df.head(15))

# -----------------------------
# DOWNLOAD BUTTON
# -----------------------------
csv = st.session_state.df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇️ Download Full Dataset (CSV)",
    data=csv,
    file_name="dataset.csv",
    mime="text/csv"
)
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
