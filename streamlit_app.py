import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Business Analytics Learning System")

# -----------------------------
# DATA GENERATION
# -----------------------------
np.random.seed(42)
n = 200

df = pd.DataFrame({
    "body_temp": np.random.normal(98.6, 1.2, n),
    "heart_rate": np.random.normal(72, 10, n),
    "oxygen": np.random.normal(96, 2, n),
    "age": np.random.randint(20, 70, n),
    "bp": np.random.normal(120, 15, n),
    "region": np.random.choice(["East", "West", "North"], n),
    "gender": np.random.choice(["Male", "Female"], n)
})

# -----------------------------
# SESSION STATE
# -----------------------------
if "question" not in st.session_state:
    st.session_state.question = None

# -----------------------------
# UI
# -----------------------------
st.title("📊 Business Analytics Learning System")

name = st.text_input("Student Name")
difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])

# -----------------------------
# QUESTION GENERATOR
# -----------------------------
def generate_hypothesis_question():

    var = "body_temp"
    group_var = "heart_rate"

    df["group"] = np.where(df[group_var] > 75, "High", "Low")

    g1 = df[df["group"] == "High"][var]
    g2 = df[df["group"] == "Low"][var]

    # STEP 1: NORMALITY
    p1 = stats.shapiro(g1)[1]
    p2 = stats.shapiro(g2)[1]

    normal = (p1 > 0.05) and (p2 > 0.05)

    # STEP 2: VARIANCE TEST
    levene_p = stats.levene(g1, g2)[1]
    equal_var = levene_p > 0.05

    # STEP 3: SELECT TEST
    if not normal:
        test_used = "Mann-Whitney U"
        stat, pval = stats.mannwhitneyu(g1, g2)
    else:
        if equal_var:
            test_used = "Independent t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=True)
        else:
            test_used = "Welch t-test"
            stat, pval = stats.ttest_ind(g1, g2, equal_var=False)

    question_text = f"""
Split data:

- Group 1: heart_rate > 75  
- Group 2: heart_rate ≤ 75  

Test whether **body temperature differs between groups**

👉 Enter approximate p-value
"""

    explanation = f"""
### Step 1: Check normality
- p1 = {round(p1,3)}, p2 = {round(p2,3)}

### Step 2: Variance test
- Levene p = {round(levene_p,3)}

### Step 3: Decision
- Normal: {normal}
- Equal variance: {equal_var}

### Final Test Used:
👉 {test_used}

### Final p-value:
👉 {round(pval,4)}
"""

    return {
        "q": question_text,
        "answer": pval,
        "explanation": explanation
    }

# -----------------------------
# GENERATE QUESTION
# -----------------------------
if st.session_state.question is None:
    st.session_state.question = generate_hypothesis_question()

q = st.session_state.question

# -----------------------------
# DISPLAY QUESTION
# -----------------------------
st.subheader("Module: Hypothesis Testing")
st.write(q["q"])

ans = st.number_input("Enter Answer", step=0.01)

# -----------------------------
# SUBMIT BUTTON
# -----------------------------
if st.button("Submit"):

    correct_val = q["answer"]

    if abs(ans - correct_val) < 0.02:
        st.success("✅ Correct")

        st.session_state.question = None
        st.rerun()

    else:
        st.error("❌ Incorrect")

        st.write("### 🔍 What went wrong")

        st.write(f"""
**Your Answer:** {ans}  
**Expected (approx):** {round(correct_val, 3)}

---

### 📘 Concept Explanation
{q["explanation"]}

---

### 🧠 Why your answer is incorrect:

- You may have selected the wrong statistical test  
- Or skipped normality / variance checks  
- Or computed using incorrect subset  

---

### ✅ What you should do:

1. Check normality (Shapiro-Wilk)
2. Check variance (Levene)
3. Choose correct test:
   - Non-normal → Mann-Whitney
   - Normal + equal variance → t-test
   - Normal + unequal variance → Welch
4. Compute p-value again

---

👉 Try again.
""")
