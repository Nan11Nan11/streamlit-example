import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics Learning System", layout="wide")
if "module_index" not in st.session_state:
    st.session_state.module_index = 0
modules = ["descriptive", "hypothesis", "regression"]
if "question_step" not in st.session_state:
    st.session_state.question_step = 0
# -----------------------------
# SESSION INIT
# -----------------------------

if "df" not in st.session_state:
    st.session_state.df = None
if "question" not in st.session_state:
    st.session_state.question = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "correct" not in st.session_state:
    st.session_state.correct = None

# -----------------------------
# DATASET GENERATOR
# -----------------------------
def generate_dataset():
    np.random.seed()

    n = 120

    heart_rate = np.random.normal(72, 8, n)
    gender = np.random.choice(["Male", "Female"], n)

    # Create relationship: higher HR → slightly higher temp
    body_temp = 97 + (heart_rate - 70)*0.03 + np.random.normal(0, 0.3, n)

    df = pd.DataFrame({
        "HeartRate": np.round(heart_rate, 0),
        "BodyTemp": np.round(body_temp, 3),
        "Gender": gender
    })

    return df

# -----------------------------
# QUESTION GENERATOR
# -----------------------------
# -----------------------------
# DESCRIPTIVE STATS
# -----------------------------
def generate_descriptive_question(df):

    col = np.random.choice(["HeartRate", "BodyTemp"])

    mean_val = df[col].mean()

    return {
        "question": f"What is the approximate mean of {col}?",
        "type": "numeric",
        "answer": round(mean_val, 2),
        "explanation": f"Mean of {col} = {round(mean_val,2)}"
    }


# -----------------------------
# HYPOTHESIS TESTING
# -----------------------------
def generate_hypothesis_question(df):

    g1 = df[df["HeartRate"] > 75]["BodyTemp"]
    g2 = df[df["HeartRate"] <= 75]["BodyTemp"]

    p1 = stats.shapiro(g1)[1]
    p2 = stats.shapiro(g2)[1]
    lev_p = stats.levene(g1, g2)[1]

    if p1 > 0.05 and p2 > 0.05:
        if lev_p > 0.05:
            test = "Student t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=True)
        else:
            test = "Welch t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=False)
    else:
        test = "Mann-Whitney U"
        stat, pval = stats.mannwhitneyu(g1, g2)

    return {
        "question": """
Split data:

Group 1: HeartRate > 75  
Group 2: HeartRate ≤ 75  

Test if BodyTemp differs.

👉 Enter approximate p-value
""",
        "type": "numeric",
        "answer": round(pval, 4),
        "explanation": f"""
Test used: {test}

Normality p-values:
Group1: {round(p1,4)}, Group2: {round(p2,4)}

Levene p-value: {round(lev_p,4)}

Final p-value: {round(pval,4)}
"""
    }


# -----------------------------
# REGRESSION
# -----------------------------
def generate_regression_question(df):

    x = df["HeartRate"]
    y = df["BodyTemp"]

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    return {
        "question": "What is the approximate slope of regression: BodyTemp ~ HeartRate?",
        "type": "numeric",
        "answer": round(slope, 3),
        "explanation": f"Slope = {round(slope,3)} (change in BodyTemp per unit HeartRate)"
    }
# -----------------------------
# MASTER QUESTION ROUTER (ADD THIS)
# -----------------------------
def generate_question(df):

    module = modules[st.session_state.module_index]
    level = difficulty

    # ---------------- DESCRIPTIVE ----------------
    if module == "descriptive":

        if level == "Easy":
            return generate_descriptive_question(df)

        elif level == "Medium":
            col = "BodyTemp"
            subset = df[df["Gender"] == "Male"]
            val = subset[col].mean()

            return {
                "question": "Compute mean BodyTemp for Male (approx)",
                "type": "numeric",
                "answer": round(val, 2),
                "explanation": f"Mean (Male) = {round(val,2)}"
            }

        else:  # HARD
            sd1 = df["HeartRate"].std()
            sd2 = df["BodyTemp"].std()

            correct = "HeartRate" if sd1 > sd2 else "BodyTemp"

            return {
                "question": "Which variable has higher variability?",
                "type": "mcq",
                "options": ["HeartRate", "BodyTemp"],
                "answer": correct,
                "explanation": "Compare standard deviations"
            }

    # ---------------- HYPOTHESIS ----------------
    elif module == "hypothesis":

        g1 = df[df["HeartRate"] > 75]["BodyTemp"]
        g2 = df[df["HeartRate"] <= 75]["BodyTemp"]

        p1 = stats.shapiro(g1)[1]
        p2 = stats.shapiro(g2)[1]
        lev_p = stats.levene(g1, g2)[1]

        if p1 > 0.05 and p2 > 0.05:
            if lev_p > 0.05:
                test = "Student t-test"
                stat, pval = stats.ttest_ind(g1, g2, equal_var=True)
            else:
                test = "Welch t-test"
                stat, pval = stats.ttest_ind(g1, g2, equal_var=False)
        else:
            test = "Mann-Whitney U"
            stat, pval = stats.mannwhitneyu(g1, g2)

        if level == "Easy":
            return {
                "question": "Which test is appropriate?",
                "type": "mcq",
                "options": ["t-test", "Mann-Whitney", "ANOVA"],
                "answer": "t-test",
                "explanation": "Two-group comparison"
            }

        elif level == "Medium":
            return {
                "question": "Enter p-value (approx)",
                "type": "numeric",
                "answer": round(pval, 4),
                "explanation": f"Test used: {test}, p-value ≈ {round(pval,4)}"
            }

        else:
            return {
                "question": "Is result statistically significant at 5%?",
                "type": "mcq",
                "options": ["Yes", "No"],
                "answer": "Yes" if pval < 0.05 else "No",
                "explanation": f"p-value = {round(pval,4)}"
            }

    # ---------------- REGRESSION ----------------
    else:

        x = df["HeartRate"]
        y = df["BodyTemp"]

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        if level == "Easy":
            return {
                "question": "What is the slope of regression?",
                "type": "numeric",
                "answer": round(slope, 3),
                "explanation": f"Slope = {round(slope,3)}"
            }

        elif level == "Medium":
            return {
                "question": "Is relationship positive or negative?",
                "type": "mcq",
                "options": ["Positive", "Negative"],
                "answer": "Positive" if slope > 0 else "Negative",
                "explanation": "Sign of slope determines direction"
            }

        else:
            return {
                "question": "Is relationship statistically significant?",
                "type": "mcq",
                "options": ["Yes", "No"],
                "answer": "Yes" if p_value < 0.05 else "No",
                "explanation": f"p-value = {round(p_value,4)}"
            }

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Business Analytics Learning System")

student = st.text_input("Student Name", "ABC123")
difficulty = st.selectbox(
    "Select Difficulty",
    ["Easy", "Medium", "Hard"]
)
# -----------------------------
# START SESSION
# -----------------------------
if st.button("🚀 Start New Session"):

    st.session_state.df = generate_dataset()
    st.session_state.question = generate_question(st.session_state.df)

    st.session_state.answered = False
    st.session_state.correct = None

    st.success("New dataset generated for this session")

# -----------------------------
# SHOW DATASET
# -----------------------------
if st.session_state.df is not None:

    st.subheader("Dataset (Use this for analysis)")
    st.dataframe(st.session_state.df.head(15), use_container_width=True)

# -----------------------------
# QUESTION BLOCK
# -----------------------------
if st.session_state.question:

    q = st.session_state.question

    # 🔒 SAFETY CHECK (ADD HERE)
    if "question" not in q:
        st.error("Question not generated properly. Please restart session.")
        st.stop()

    st.subheader("Current Question")
    st.write(q["question"])

    if q["type"] == "numeric":
        user_ans = st.number_input("Enter answer", value=0.0)
    else:
        user_ans = st.radio("Select answer", q["options"])

    # -----------------------------
    # SUBMIT
    # -----------------------------
    if st.button("Submit"):

        if q["type"] == "numeric":
            tol = 0.02
            st.session_state.correct = abs(user_ans - q["answer"]) <= tol
        else:
            st.session_state.correct = user_ans == q["answer"]
    
        st.session_state.answered = True
    st.rerun()
    st.session_state.user_ans = user_ans
# -----------------------------
# RESULT
# -----------------------------
if st.session_state.answered:

    q = st.session_state.question

    if st.session_state.correct:
        st.success("Correct ✅")
    else:
        st.error("Incorrect ❌")
        st.write(f"Your answer: {user_ans}")
        st.write(f"Correct answer: {q['answer']}")

    # -----------------------------
    # EXPLANATION
    # -----------------------------
    st.markdown("### 🔍 Explanation")

    st.write(q["explanation"])
st.write(f"Your answer: {st.session_state.user_ans}")
    # -----------------------------
    # NEXT QUESTION
    # -----------------------------
    if st.button("Next Question"):

    # 👉 PROGRESSION LOGIC (ADD THIS)
        if st.session_state.correct:
            st.session_state.question_step += 1
    
            # move to next module after 2 correct answers
            if st.session_state.question_step >= 2:
                st.session_state.module_index += 1
                st.session_state.question_step = 0
    
                if st.session_state.module_index >= len(modules):
                    st.success("🎓 All modules completed!")
                    st.stop()

        st.session_state.question = generate_question(st.session_state.df)
        st.session_state.answered = False
        st.session_state.correct = None

        st.rerun()
