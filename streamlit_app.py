import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Business Analytics LMS", layout="wide")

st.title("📊 Business Analytics LMS")

mode = st.sidebar.selectbox("Select Mode", ["Student", "Instructor"])

# =====================================================
# STUDENT MODE
# =====================================================
if mode == "Student":

    st.header("👩‍🎓 Student Portal")

    name = st.text_input("Enter Name")
    student_id = st.text_input("Enter Student ID")

    # -----------------------------
    # DATASET GENERATION FUNCTION
    # -----------------------------
    def generate_dataset(seed):
        np.random.seed(seed)
        data = pd.DataFrame({
            "X1": np.random.normal(50, 10, 100),
            "X2": np.random.normal(50, 3, 100),
            "X3": np.random.normal(50, 25, 100),
            "X4": np.random.lognormal(3, 0.5, 100)
        })
        return data.round(2)

    # -----------------------------
    # GENERATE DATASET BUTTON
    # -----------------------------
    if st.button("Generate Dataset"):

        if student_id == "":
            st.warning("Please enter Student ID")
        else:
            seed = sum([ord(c) for c in student_id])
            df = generate_dataset(seed)

            st.session_state["data"] = df
            st.success("Dataset generated successfully!")

    # -----------------------------
    # SHOW DATASET
    # -----------------------------
    if "data" in st.session_state:

        df = st.session_state["data"]

        st.subheader("📊 Your Dataset (first 10 rows)")
        st.dataframe(df.head(10))

        # =====================================================
        # FULL QUIZ
        # =====================================================
        st.subheader("🧪 Full Quiz")

        responses = {}

        # Q1
        st.markdown("### Q1: Compute Mean of X1")
        responses["Q1"] = st.number_input("Enter Mean of X1")

        # Q2
        st.markdown("### Q2: Compute Standard Deviation of X3")
        responses["Q2"] = st.number_input("Enter SD of X3")

        # Q3
        st.markdown("### Q3: Which variable is most volatile? Explain")
        responses["Q3"] = st.text_area("Answer")

        # Q4
        st.markdown("### Q4: When is median preferred over mean?")
        responses["Q4"] = st.text_area("Answer")

        # Q5
        st.markdown("### Q5: Coefficient of Variation measures:")
        responses["Q5"] = st.radio(
            "Choose one:",
            ["Central tendency", "Dispersion", "Skewness"]
        )

        # Q6
        st.markdown("### Q6: Identify skewness of X4")
        responses["Q6"] = st.text_area("Answer")

        # Q7
        st.markdown("### Q7: If p-value > 0.05, data is?")
        responses["Q7"] = st.radio(
            "Choose one:",
            ["Normal", "Not normal"]
        )

        # Q8
        st.markdown("### Q8: How do you compute probability using normal distribution?")
        responses["Q8"] = st.text_area("Answer")

        # =====================================================
        # SUBMIT BUTTON
        # =====================================================
        if st.button("Submit Full Quiz"):

            st.subheader("📘 Marking Scheme (Rubric)")
            st.write("• Each question = 1 mark")
            st.write("• Numerical accuracy → 0.5")
            st.write("• Interpretation → 0.5")
            st.write("• Maximum Marks: 8")

            st.subheader("📊 Evaluation Summary")

            total_score = 0

            correct_mean = df["X1"].mean()
            correct_sd = df["X3"].std()
            cv = df.std() / df.mean()
            most_volatile = cv.idxmax()

            # -----------------------------
            # Q1
            # -----------------------------
            st.markdown("### Q1 Feedback")
            if abs(responses["Q1"] - correct_mean) < 0.5:
                st.success("✅ Correct")
                total_score += 1
            else:
                st.error(f"❌ Incorrect. Correct: {round(correct_mean,2)}")

            # -----------------------------
            # Q2
            # -----------------------------
            st.markdown("### Q2 Feedback")
            if abs(responses["Q2"] - correct_sd) < 0.5:
                st.success("✅ Correct")
                total_score += 1
            else:
                st.error(f"❌ Incorrect. Correct: {round(correct_sd,2)}")

            # -----------------------------
            # Q3
            # -----------------------------
            st.markdown("### Q3 Feedback")
            if most_volatile.lower() in responses["Q3"].lower():
                st.success("✅ Correct interpretation")
                total_score += 1
            else:
                st.error(f"❌ Incorrect. {most_volatile} is most volatile")

            # -----------------------------
            # Q5
            # -----------------------------
            st.markdown("### Q5 Feedback")
            if responses["Q5"] == "Dispersion":
                st.success("✅ Correct")
                total_score += 1
            else:
                st.error("❌ Incorrect. CV measures dispersion")

            # -----------------------------
            # Q7
            # -----------------------------
            st.markdown("### Q7 Feedback")
            if responses["Q7"] == "Normal":
                st.success("✅ Correct")
                total_score += 1
            else:
                st.error("❌ Incorrect. p > 0.05 ⇒ normal")

            st.subheader(f"🎯 Final Score: {total_score} / 8")


# =====================================================
# INSTRUCTOR MODE
# =====================================================
else:

    st.header("👨‍🏫 Instructor Dashboard")

    uploaded_files = st.file_uploader(
        "Upload student Excel files",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} files uploaded")
