import streamlit as st
import pandas as pd
import numpy as np
from hashlib import md5

st.set_page_config(page_title="Business Analytics LMS", layout="wide")

st.title("📊 Business Analytics LMS")

mode = st.sidebar.selectbox("Select Mode", ["Student", "Instructor"])

# ---------------------------
# STUDENT MODE
# ---------------------------
st.subheader("🧪 Full Quiz")

responses = {}

# ----------------------
# Q1 Mean
# ----------------------
st.markdown("### Q1: Compute Mean of X1 (Numerical)")
responses["Q1"] = st.number_input("Enter Mean of X1")

# ----------------------
# Q2 SD
# ----------------------
st.markdown("### Q2: Compute Standard Deviation of X3 (Numerical)")
responses["Q2"] = st.number_input("Enter SD of X3")

# ----------------------
# Q3 CV Interpretation
# ----------------------
st.markdown("### Q3: Which variable is most volatile? (Interpretation)")
responses["Q3"] = st.text_area("Explain your answer")

# ----------------------
# Q4 Concept (Mean vs Median)
# ----------------------
st.markdown("### Q4: When is median preferred over mean?")
responses["Q4"] = st.text_area("Answer")

# ----------------------
# Q5 MCQ
# ----------------------
st.markdown("### Q5: Coefficient of Variation measures:")
responses["Q5"] = st.radio(
    "Choose one:",
    ["Central tendency", "Dispersion", "Skewness"]
)

# ----------------------
# Q6 Skew
# ----------------------
st.markdown("### Q6: Identify skewness of X4")
responses["Q6"] = st.text_area("Is it positive/negative? Explain")

# ----------------------
# Q7 Normality
# ----------------------
st.markdown("### Q7: If p-value > 0.05, data is?")
responses["Q7"] = st.radio(
    "Choose one:",
    ["Normal", "Not normal"]
)

# ----------------------
# Q8 Probability
# ----------------------
st.markdown("### Q8: Compute probability using normal distribution (conceptual)")
responses["Q8"] = st.text_area("Explain how you would compute it")

# ----------------------
# SUBMIT
# ----------------------
if st.button("Submit Full Quiz"):

    st.subheader("📊 Evaluation Summary")

    total_score = 0

    # Correct values
    correct_mean = df["X1"].mean()
    correct_sd = df["X3"].std()
    cv = df.std() / df.mean()
    most_volatile = cv.idxmax()

    # ----------------------
    # Q1
    # ----------------------
    st.markdown("### Q1 Feedback")
    if abs(responses["Q1"] - correct_mean) < 0.5:
        st.success("Correct")
        total_score += 1
    else:
        st.error(f"Incorrect. Correct: {round(correct_mean,2)}")

    # ----------------------
    # Q2
    # ----------------------
    st.markdown("### Q2 Feedback")
    if abs(responses["Q2"] - correct_sd) < 0.5:
        st.success("Correct")
        total_score += 1
    else:
        st.error(f"Incorrect. Correct: {round(correct_sd,2)}")

    # ----------------------
    # Q3
    # ----------------------
    st.markdown("### Q3 Feedback")
    if most_volatile.lower() in responses["Q3"].lower():
        st.success("Correct interpretation")
        total_score += 1
    else:
        st.error(f"Incorrect. {most_volatile} is most volatile")

    # ----------------------
    # Q5
    # ----------------------
    st.markdown("### Q5 Feedback")
    if responses["Q5"] == "Dispersion":
        st.success("Correct")
        total_score += 1
    else:
        st.error("Incorrect. CV measures dispersion")

    # ----------------------
    # Q7
    # ----------------------
    st.markdown("### Q7 Feedback")
    if responses["Q7"] == "Normal":
        st.success("Correct")
        total_score += 1
    else:
        st.error("Incorrect. p > 0.05 ⇒ normal")

    st.subheader(f"🎯 Final Score: {total_score} / 8")
# ---------------------------
# INSTRUCTOR MODE (OLD APP)
# ---------------------------
else:

    st.header("👨‍🏫 Instructor Dashboard")

    uploaded_files = st.file_uploader(
        "Upload student Excel files",
        accept_multiple_files=True
    )

    results = []

    if uploaded_files:

        for file in uploaded_files:

            try:
                df = pd.read_excel(file, sheet_name="DATA")

                score = np.random.choice([0, 0.5, 1])  # placeholder

                results.append({
                    "Student": file.name,
                    "Score": score
                })

            except Exception as e:
                st.error(f"Error: {e}")

        st.dataframe(pd.DataFrame(results))
