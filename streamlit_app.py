import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics Learning System")

# -------------------------------
# RESET SESSION BUTTON
# -------------------------------
if st.sidebar.button("🔄 Start New Session"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# -------------------------------
# DATA GENERATION (ONCE PER SESSION)
# -------------------------------
if "df" not in st.session_state:

    np.random.seed(np.random.randint(0, 100000))

    n = 120

    heart_rate = np.random.normal(72, 8, n).round()
    body_temp = 98 + (heart_rate - 72)*0.05 + np.random.normal(0, 0.5, n)
    gender = np.random.choice(["Male", "Female"], n)

    df = pd.DataFrame({
        "HeartRate": heart_rate,
        "BodyTemp": body_temp,
        "Gender": gender
    })

    df["HT_GT_75"] = (df["HeartRate"] > 75).astype(int)

    st.session_state.df = df

df = st.session_state.df

# -------------------------------
# UI
# -------------------------------
st.title("📊 Business Analytics Learning System")

name = st.text_input("Student Name")
difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

# -------------------------------
# QUESTION ENGINE
# -------------------------------
def generate_question():

    # ---------------- EASY ----------------
    if difficulty == "Easy":

        return {
            "type": "mcq",
            "q": "Which variable is numeric?",
            "options": ["HeartRate", "Gender"],
            "answer": "HeartRate",
            "explanation": "HeartRate is numeric. Gender is categorical."
        }

    # ---------------- MEDIUM ----------------
    elif difficulty == "Medium":

        var = np.random.choice(["HeartRate", "BodyTemp"])
        true_val = df[var].std()

        return {
            "type": "numeric",
            "q": f"Compute standard deviation of {var} (approx)",
            "answer": true_val,
            "explanation": f"SD of {var} = {round(true_val,2)}"
        }

    # ---------------- HARD ----------------
    else:

        g1 = df[df["HT_GT_75"] == 1]["BodyTemp"]
        g2 = df[df["HT_GT_75"] == 0]["BodyTemp"]

        # Step 1: Normality
        p1 = stats.shapiro(g1)[1]
        p2 = stats.shapiro(g2)[1]
        normal = (p1 > 0.05) and (p2 > 0.05)

        # Step 2: Variance test
        lev_p = stats.levene(g1, g2)[1]
        equal_var = lev_p > 0.05

        # Step 3: Choose test
        if not normal:
            test_name = "Mann-Whitney U"
            stat, pval = stats.mannwhitneyu(g1, g2)
        else:
            if equal_var:
                test_name = "Student t-test"
                stat, pval = stats.ttest_ind(g1, g2, equal_var=True)
            else:
                test_name = "Welch t-test"
                stat, pval = stats.ttest_ind(g1, g2, equal_var=False)

        return {
            "type": "numeric",
            "q": """
Split data:

Group 1: HeartRate > 75  
Group 2: HeartRate ≤ 75  

Test whether BodyTemp differs.

👉 Enter approximate p-value
""",
            "answer": pval,
            "explanation": f"""
Step 1: Normality  
p-values = {round(p1,3)}, {round(p2,3)}

Step 2: Variance (Levene)  
p = {round(lev_p,3)}

Step 3: Test selected  
👉 {test_name}

Final p-value ≈ {round(pval,5)}
"""
        }

# -------------------------------
# STORE QUESTION
# -------------------------------
if "question" not in st.session_state:
    st.session_state.question = generate_question()

q = st.session_state.question

# -------------------------------
# DISPLAY QUESTION
# -------------------------------
st.subheader("Current Module")
st.write(q["q"])

# -------------------------------
# INPUT
# -------------------------------
if q["type"] == "mcq":
    user_ans = st.radio("Select answer", q["options"])

elif q["type"] == "numeric":
    user_ans = st.number_input("Enter answer", step=0.01)

# -------------------------------
# SUBMIT BUTTON
# -------------------------------
if st.button("Submit"):

    correct = q["answer"]

    # ---------- MCQ ----------
    if q["type"] == "mcq":

        if user_ans == correct:
            st.success("✅ Correct")
            st.session_state.question = generate_question()
            st.rerun()
        else:
            st.error("❌ Incorrect")
            st.write(q["explanation"])

    # ---------- NUMERIC ----------
    else:

        tolerance = max(0.05, abs(correct)*0.1)

        if abs(user_ans - correct) <= tolerance:
            st.success("✅ Correct")
            st.session_state.question = generate_question()
            st.rerun()

        else:
            st.error("❌ Incorrect")

            st.write(f"""
### 🔍 What went wrong

Your Answer: {user_ans}  
Correct Answer (approx): {round(correct,5)}

---

{q["explanation"]}
""")
