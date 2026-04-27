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

    st.header("👩‍🎓 Student Quiz Agent")

    name = st.text_input("Enter Name")
    student_id = st.text_input("Enter Student ID")

    # ----------------------------
    # DATASET GENERATION
    # ----------------------------
    def generate_dataset(seed):
        np.random.seed(seed)
        return pd.DataFrame({
            "X1": np.random.normal(50, 10, 100),
            "X2": np.random.normal(50, 5, 100),
            "X3": np.random.normal(50, 20, 100),
        }).round(2)

    if st.button("Generate Dataset"):
        if student_id == "":
            st.warning("Enter Student ID")
        else:
            seed = sum([ord(c) for c in student_id])
            st.session_state["data"] = generate_dataset(seed)
            st.session_state["streak"] = 0
            st.success("Dataset generated")

    # ----------------------------
    # PROCEED IF DATA EXISTS
    # ----------------------------
    if "data" in st.session_state:

        df = st.session_state["data"]

        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        # ----------------------------
        # STREAK MODE
        # ----------------------------
        st.subheader("🔥 Streak Mode (3 correct needed)")

        if "streak" not in st.session_state:
            st.session_state["streak"] = 0

        st.write(f"Current Streak: {st.session_state['streak']} / 3")

        qtype = np.random.choice(["mean", "sd", "concept"])

        if qtype == "mean":
            ans = st.number_input("Mean of X1", key="s1")

            if st.button("Submit Streak", key="sb1"):
                correct = df["X1"].mean()
                if abs(ans - correct) < 0.5:
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"Wrong. Correct mean ≈ {round(correct,2)}")
                    st.session_state["streak"] = 0

        elif qtype == "sd":
            ans = st.number_input("SD of X3", key="s2")

            if st.button("Submit Streak", key="sb2"):
                correct = df["X3"].std()
                if abs(ans - correct) < 0.5:
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"Wrong. Correct SD ≈ {round(correct,2)}")
                    st.session_state["streak"] = 0

        else:
            ans = st.radio(
                "CV measures:",
                ["Central tendency", "Dispersion", "Skewness"],
                key="s3"
            )

            if st.button("Submit Streak", key="sb3"):
                if ans == "Dispersion":
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error("Wrong. CV measures dispersion")
                    st.session_state["streak"] = 0

        # ----------------------------
        # FULL QUIZ
        # ----------------------------
        if st.session_state["streak"] >= 3:

            st.success("Unlocked Full Quiz")

            st.subheader("🧪 Quiz")

            responses = {}

            responses["Q1_num"] = st.number_input("Q1: Mean of X1", key="q1n")
            responses["Q1_txt"] = st.text_area("Explain mean", key="q1t")

            responses["Q2_num"] = st.number_input("Q2: SD of X3", key="q2n")
            responses["Q2_txt"] = st.text_area("Explain SD", key="q2t")

            responses["Q3_txt"] = st.text_area("Most volatile variable?", key="q3")

            responses["Q4"] = st.radio(
                "CV measures:",
                ["Central tendency", "Dispersion", "Skewness"],
                key="q4"
            )

            if st.button("Submit Quiz", key="submit_quiz"):

                results = []
                total = 0

                mean_x1 = df["X1"].mean()
                sd_x3 = df["X3"].std()
                cv = df.std() / df.mean()
                most_vol = cv.idxmax()

                # Q1
                q1 = 0
                fb = ""
                if abs(responses["Q1_num"] - mean_x1) < 0.5:
                    q1 += 0.5
                else:
                    fb += f"Mean incorrect (≈{round(mean_x1,2)}). "

                if "average" in responses["Q1_txt"].lower():
                    q1 += 0.5
                else:
                    fb += "Mean = average not explained."

                total += q1
                results.append(("Q1", q1, fb))

                # Q2
                q2 = 0
                fb = ""
                if abs(responses["Q2_num"] - sd_x3) < 0.5:
                    q2 += 0.5
                else:
                    fb += f"SD incorrect (≈{round(sd_x3,2)}). "

                if "spread" in responses["Q2_txt"].lower():
                    q2 += 0.5
                else:
                    fb += "SD = spread not explained."

                total += q2
                results.append(("Q2", q2, fb))

                # Q3
                q3 = 1 if most_vol.lower() in responses["Q3_txt"].lower() else 0
                fb = "" if q3 else f"Correct answer: {most_vol}"

                total += q3
                results.append(("Q3", q3, fb))

                # Q4
                q4 = 1 if responses["Q4"] == "Dispersion" else 0
                fb = "" if q4 else "CV measures dispersion"

                total += q4
                results.append(("Q4", q4, fb))

                st.subheader("📊 Detailed Feedback")

                for q, s, f in results:
                    st.write(f"{q}: {s}/1")
                    st.write("✅ Correct" if s == 1 else f"🔴 {f}")

                percent = (total / 4) * 100

                st.subheader("Final Score")
                st.write(f"{total}/4 ({round(percent,2)}%)")

                if percent >= 80:
                    st.success("🎉 Proficiency Achieved")
                    st.balloons()
                else:
                    st.warning("Needs improvement")

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
        
