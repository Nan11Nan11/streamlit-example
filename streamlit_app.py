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
if mode == "Student":

    st.header("👩‍🎓 Student Portal")

    name = st.text_input("Enter Name")
    student_id = st.text_input("Enter Student ID")

    def generate_dataset(seed):
        np.random.seed(seed)
        data = pd.DataFrame({
            "X1": np.random.normal(50, 10, 100),
            "X2": np.random.normal(50, 3, 100),
            "X3": np.random.normal(50, 25, 100),
            "X4": np.random.lognormal(3, 0.5, 100)
        })
        return data.round(2)

    if st.button("Generate Dataset"):

        if student_id == "":
            st.warning("Please enter Student ID")
        else:
            seed = sum([ord(c) for c in student_id])
            df = generate_dataset(seed)

            st.session_state["data"] = df

            st.subheader("📊 Your Dataset")
            st.dataframe(df)

    if "data" in st.session_state:

        df = st.session_state["data"]

        st.subheader("📝 Answer the Questions")

        mean_x1 = st.number_input("Mean of X1")
        sd_x3 = st.number_input("Standard Deviation of X3")

        interpretation = st.text_area(
            "Which variable is most volatile and why?"
        )

if st.button("Submit Answers"):

    correct_mean = df["X1"].mean()
    correct_sd = df["X3"].std()
    cv = df.std() / df.mean()
    most_volatile = cv.idxmax()

    score = 0

    st.subheader("📋 Feedback")

    # ------------------------
    # MEAN CHECK
    # ------------------------
    if abs(mean_x1 - correct_mean) < 0.5:
        score += 0.5
        st.success("✅ Mean of X1 is correct")
    else:
        st.error("❌ Mean of X1 is incorrect")
        st.write(f"✔ Correct value: {round(correct_mean,2)}")
        st.write("💡 Hint: Use AVERAGE() on full X1 column")

    # ------------------------
    # SD CHECK
    # ------------------------
    if abs(sd_x3 - correct_sd) < 0.5:
        score += 0.5
        st.success("✅ Standard deviation of X3 is correct")
    else:
        st.error("❌ Standard deviation of X3 is incorrect")
        st.write(f"✔ Correct value: {round(correct_sd,2)}")
        st.write("💡 Hint: Use STDEV.S() not STDEV.P")

    # ------------------------
    # INTERPRETATION CHECK
    # ------------------------
    if most_volatile.lower() in interpretation.lower():
        score += 0.5
        st.success("✅ Correct interpretation of volatility")
    else:
        st.error("❌ Incorrect interpretation")
        st.write(f"✔ Correct answer: {most_volatile} is most volatile")
        st.write("💡 Hint: Compare coefficient of variation (SD/Mean)")

    st.subheader(f"🎯 Final Score: {score} / 1.5")
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
