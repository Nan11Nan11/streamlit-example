import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats

st.set_page_config(page_title="Business Analytics Learning System", layout="wide")

# =============================
# SESSION STATE INIT
# =============================
if "df" not in st.session_state:
    st.session_state.df = None
if "question" not in st.session_state:
    st.session_state.question = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "correct" not in st.session_state:
    st.session_state.correct = None
if "student_name" not in st.session_state:
    st.session_state.student_name = ""

# =============================
# DATA GENERATION
# =============================
def generate_dataset(n=120):

    np.random.seed()

    df = pd.DataFrame({
        "HeartRate": np.random.randint(60, 100, n),
        "BodyTemp": np.random.normal(99, 0.5, n),
        "Age": np.random.randint(20, 60, n),
        "Income": np.random.randint(30000, 100000, n),
        "StressScore": np.random.uniform(1, 10, n),
        "Gender": np.random.choice(["Male", "Female"], n),
        "ExerciseLevel": np.random.choice(["Low", "Medium", "High"], n),
        "Smoker": np.random.choice(["Yes", "No"], n)
    })

    return df

# =============================
# ANALYTICS FUNCTIONS (FULL DATA)
# =============================
def run_ttest(df):

    g1 = df[df["HeartRate"] > 75]["BodyTemp"]
    g2 = df[df["HeartRate"] <= 75]["BodyTemp"]

    stat, pval = stats.ttest_ind(g1, g2, equal_var=False)

    decision = "Reject H0" if pval < 0.05 else "Fail to Reject H0"

    return {
        "pval": pval,
        "decision": decision
    }

def run_regression(df):

    x = df["HeartRate"]
    y = df["BodyTemp"]

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    return {
        "slope": slope,
        "pval": p_value
    }

# =============================
# QUESTION GENERATOR
# =============================
def generate_question(df, difficulty):

    module = np.random.choice(["desc","hyp","reg"])

    # ---------- EASY ----------
    if difficulty == "Easy":

        col = np.random.choice(["HeartRate","BodyTemp"])
        val = df[col].mean()

        return {
            "type":"numeric",
            "question":f"What is the mean of {col}? (use full dataset)",
            "answer":round(val,2),
            "explanation":f"Mean of {col} = {round(val,2)}",
            "jamovi":None
        }

    # ---------- MEDIUM ----------
    elif difficulty == "Medium":

        if module == "hyp":
            res = run_ttest(df)
            return {
                "type":"numeric",
                "question":"Enter the p-value for difference in BodyTemp (HeartRate split)",
                "answer":round(res["pval"],4),
                "explanation":f"p-value = {round(res['pval'],4)}",
                "jamovi":("ttest",res)
            }

        else:
            res = run_regression(df)
            return {
                "type":"numeric",
                "question":"What is the regression slope (BodyTemp ~ HeartRate)?",
                "answer":round(res["slope"],3),
                "explanation":f"Slope = {round(res['slope'],3)}",
                "jamovi":("reg",res)
            }

    # ---------- HARD ----------
    else:

        if module == "hyp":
            res = run_ttest(df)
            return {
                "type":"mcq",
                "question":"What is the correct conclusion?",
                "options":["Reject H0","Fail to Reject H0"],
                "answer":res["decision"],
                "explanation":f"Decision based on p-value = {round(res['pval'],4)}",
                "jamovi":("ttest",res)
            }

        else:
            res = run_regression(df)
            return {
                "type":"mcq",
                "question":"Is HeartRate statistically significant?",
                "options":["Yes","No"],
                "answer":"Yes" if res["pval"] < 0.05 else "No",
                "explanation":f"p-value = {round(res['pval'],4)}",
                "jamovi":("reg",res)
            }

# =============================
# UI HEADER
# =============================
st.title("📊 Business Analytics Learning System")

student_name = st.text_input("Student Name")

difficulty = st.selectbox("Difficulty", ["Easy","Medium","Hard"])

# =============================
# START SESSION BUTTON
# =============================
if st.button("Start New Session"):

    st.session_state.df = generate_dataset()
    st.session_state.question = generate_question(st.session_state.df, difficulty)
    st.session_state.answered = False
    st.session_state.correct = None
    st.session_state.student_name = student_name

# =============================
# DISPLAY DATA
# =============================
if st.session_state.df is not None:

    df = st.session_state.df

    st.success("Dataset generated for this session")

    st.subheader("Sample Data (first 15 rows)")
    st.dataframe(df.head(15))

    # DOWNLOAD BUTTON
    csv = df.to_csv(index=False).encode("utf-8")

    filename = f"{student_name if student_name else 'student'}_dataset.csv"

    st.download_button(
        "⬇ Download Full Dataset",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

    st.info("⚠️ Use FULL dataset for calculations (Jamovi / Excel)")

# =============================
# QUESTION
# =============================
if st.session_state.question:

    q = st.session_state.question

    st.subheader("Current Question")
    st.write(q["question"])

    user_ans = None

    if q["type"] == "numeric":
        user_ans = st.number_input("Enter answer", format="%.4f")

    else:
        user_ans = st.radio("Select answer", q["options"])

    if st.button("Submit"):

        if q["type"] == "numeric":
            correct = abs(user_ans - q["answer"]) < 0.01
        else:
            correct = user_ans == q["answer"]

        st.session_state.answered = True
        st.session_state.correct = correct

    # =============================
    # RESULTS
    # =============================
    if st.session_state.answered:

        if st.session_state.correct:
            st.success("Correct ✅")
        else:
            st.error("Incorrect ❌")
            st.write(f"Your answer: {user_ans}")
            st.write(f"Correct answer: {q['answer']}")

        st.markdown("### 🔍 Explanation")
        st.write(q["explanation"])

        # =============================
        # JAMOVI STYLE OUTPUT
        # =============================
        if q["jamovi"]:

            kind, res = q["jamovi"]

            st.markdown("### 📊 Jamovi Output (Simplified)")

            if kind == "ttest":
                st.code(f"""
Independent Samples T-Test

p-value: {round(res['pval'],4)}
Decision: {res['decision']}
""")

            if kind == "reg":
                st.code(f"""
Linear Regression

Slope: {round(res['slope'],3)}
p-value: {round(res['pval'],4)}
""")

        # =============================
        # NEXT QUESTION
        # =============================
        if st.button("Next Question"):

            st.session_state.question = generate_question(
                st.session_state.df,
                difficulty
            )
            st.session_state.answered = False
            st.session_state.correct = None

            st.rerun()
