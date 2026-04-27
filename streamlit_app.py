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
            st.success("Dataset generated successfully!")

    # ===============================
    # ONLY PROCEED IF DATA EXISTS
    # ===============================
    if "data" in st.session_state:

        df = st.session_state["data"]

        st.subheader("📊 Your Dataset (first 10 rows)")
        st.dataframe(df.head(10))

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Dataset",
            data=csv,
            file_name="dataset.csv",
            mime="text/csv"
        )

        # ===============================
        # STREAK MODE
        # ===============================
        st.subheader("🔥 Streak Mode (Get 3 correct in a row)")

        if "streak" not in st.session_state:
            st.session_state["streak"] = 0

        st.write(f"Current Streak: {st.session_state['streak']} / 3")

        question_type = np.random.choice(["mean", "sd", "concept"])

        if question_type == "mean":
            ans = st.number_input("Compute Mean of X1", key="streak_mean")

            if st.button("Submit Streak", key="b1"):
                correct = df["X1"].mean()
                if abs(ans - correct) < 0.5:
                    st.success("Correct!")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"Wrong! Correct: {round(correct,2)}")
                    st.session_state["streak"] = 0

        elif question_type == "sd":
            ans = st.number_input("Compute SD of X3", key="streak_sd")

            if st.button("Submit Streak", key="b2"):
                correct = df["X3"].std()
                if abs(ans - correct) < 0.5:
                    st.success("Correct!")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"Wrong! Correct: {round(correct,2)}")
                    st.session_state["streak"] = 0

        else:
            ans = st.radio(
                "Coefficient of variation measures:",
                ["Central tendency", "Dispersion", "Skewness"],
                key="streak_mcq"
            )

            if st.button("Submit Streak", key="b3"):
                if ans == "Dispersion":
                    st.success("Correct!")
                    st.session_state["streak"] += 1
                else:
                    st.error("Wrong!")
                    st.session_state["streak"] = 0

        # ===============================
        # FULL QUIZ (ONLY AFTER STREAK)
        # ===============================
        if st.session_state["streak"] >= 3:

            st.success("🎉 Streak completed! Full quiz unlocked!")

            st.subheader("🧪 Full Quiz")

            responses = {}

            responses["Q1"] = st.number_input("Mean X1")
            responses["Q2"] = st.number_input("SD X3")
            responses["Q3"] = st.text_area("Answer Q3", key="q3")

            responses["Q5"] = st.radio(
                "CV measures:",
                ["Central tendency", "Dispersion", "Skewness"]
            )

            if st.button("Submit Full Quiz"):

                total = 0

                correct_mean = df["X1"].mean()
                correct_sd = df["X3"].std()
                cv = df.std() / df.mean()
                most_vol = cv.idxmax()

                if abs(responses["Q1"] - correct_mean) < 0.5:
                    total += 1

                if abs(responses["Q2"] - correct_sd) < 0.5:
                    total += 1

                if most_vol.lower() in responses["Q3"].lower():
                    total += 1

                if responses["Q5"] == "Dispersion":
                    total += 1

                max_marks = 4
                percentage = (total / max_marks) * 100

                st.subheader("📊 Result Summary")
                st.write(f"Score: {total} / {max_marks}")
                st.write(f"Percentage: {round(percentage,2)}%")

                if percentage >= 80:
                    st.success("🎉 PROFICIENCY ACHIEVED!")
                    st.balloons()
                else:
                    st.warning("❌ Proficiency not achieved")

        else:
            st.info("🔒 Complete streak (3 correct answers) to unlock quiz")

# =====================================================
# INSTRUCTOR MODE
# =====================================================
elif mode == "Instructor":

    st.header("👨‍🏫 Instructor Dashboard")

    uploaded_files = st.file_uploader(
        "Upload student Excel files",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} files uploaded")
