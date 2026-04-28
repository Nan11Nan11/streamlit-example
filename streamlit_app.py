import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics Learning System")

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Business Analytics Learning System")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "started" not in st.session_state:
    st.session_state.started = False

if "df" not in st.session_state:
    st.session_state.df = None

if "question" not in st.session_state:
    st.session_state.question = None

# -----------------------------
# STUDENT INPUT
# -----------------------------
name = st.text_input("Student Name")
difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

# -----------------------------
# START SESSION BUTTON
# -----------------------------
if not st.session_state.started:

    if st.button("▶️ Start Session"):

        # ✅ Generate NEW dataset ONLY HERE
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
        st.session_state.started = True

        st.rerun()

    st.stop()

# -----------------------------
# RESET SESSION
# -----------------------------
if st.sidebar.button("🔄 Start New Session"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# -----------------------------
# LOAD DATA
# -----------------------------
df = st.session_state.df

st.success("✅ Dataset generated for this session")

# -----------------------------
# QUESTION ENGINE
# -----------------------------
def generate_question():

    # -------- EASY --------
    if difficulty == "Easy":

        return {
            "type": "mcq",
            "q": "Which variable is numeric?",
            "options": ["HeartRate", "Gender"],
            "answer": "HeartRate",
            "explanation": "HeartRate is numeric. Gender is categorical."
        }

    # -------- MEDIUM --------
    elif difficulty == "Medium":

        var = np.random.choice(["HeartRate", "BodyTemp"])
        val = df[var].std()

        return {
            "type": "numeric",
            "q": f"Compute standard deviation of {var} (approx)",
            "answer": val,
            "explanation": f"SD of {var} ≈ {round(val,2)}"
        }

    # -------- HARD --------
    else:

        g1 = df[df["HT_GT_75"] == 1]["BodyTemp"]
        g2 = df[df["HT_GT_75"] == 0]["BodyTemp"]

        p1 = stats.shapiro(g1)[1]
        p2 = stats.shapiro(g2)[1]
        normal = (p1 > 0.05) and (p2 > 0.05)

        lev_p = stats.levene(g1, g2)[1]
        equal_var = lev_p > 0.05

        if not normal:
            test = "Mann-Whitney U"
            _, pval = stats.mannwhitneyu(g1, g2)
        else:
            if equal_var:
                test = "Student t-test"
                _, pval = stats.ttest_ind(g1, g2, equal_var=True)
            else:
                test = "Welch t-test"
                _, pval = stats.ttest_ind(g1, g2, equal_var=False)

        return {
            "type": "numeric",
            "q": """
Split data:

Group 1: HeartRate > 75  
Group 2: HeartRate ≤ 75  

Test if BodyTemp differs.

👉 Enter approximate p-value
""",
            "answer": pval,
            "explanation": f"""
Normality p-values: {round(p1,3)}, {round(p2,3)}
Levene p-value: {round(lev_p,3)}

Selected Test: {test}

Final p-value ≈ {round(pval,5)}
"""
        }

# -----------------------------
# LOAD QUESTION
# -----------------------------
if st.session_state.question is None:
    st.session_state.question = generate_question()

q = st.session_state.question

# -----------------------------
# DISPLAY
# -----------------------------
st.subheader("Current Module")
st.write(q["q"])

# -----------------------------
# INPUT
# -----------------------------
if q["type"] == "mcq":
    ans = st.radio("Select answer", q["options"])

else:
    ans = st.number_input("Enter answer", step=0.01)

# -----------------------------
# SUBMIT
# -----------------------------
if st.button("Submit"):

    correct = q["answer"]

    # MCQ
    if q["type"] == "mcq":

        if ans == correct:
            st.success("✅ Correct")
            st.session_state.question = generate_question()
            st.rerun()
        else:
            st.error("❌ Incorrect")
            st.write(q["explanation"])

    # NUMERIC
    else:

        tol = max(0.05, abs(correct)*0.1)

        if abs(ans - correct) <= tol:
            st.success("✅ Correct")
            st.session_state.question = generate_question()
            st.rerun()
        else:
            st.error("❌ Incorrect")

            st.write(f"""
### 🔍 What went wrong

Your Answer: {ans}  
Correct (approx): {round(correct,5)}

---

{q["explanation"]}
""")
