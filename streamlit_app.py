import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Business Analytics LMS", layout="wide")

st.title("📊 Business Analytics LMS")

mode = st.sidebar.selectbox("Select Mode", ["Student", "Instructor"])

# =====================================================
# STUDENT MODE
# =====================================================
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

            if st.button("Submit Streak"):
                correct = df["X1"].mean()
                if abs(ans - correct) < 0.5:
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"Wrong. Correct mean ≈ {round(correct,2)}")
                    st.session_state["streak"] = 0

        elif qtype == "sd":
            ans = st.number_input("SD of X3", key="s2")

            if st.button("Submit Streak"):
                correct = df["X3"].std()
                if abs(ans - correct) < 0.5:
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"Wrong. Correct SD ≈ {round(correct,2)}")
                    st.session_state["streak"] = 0

        else:
            ans = st.radio("CV measures:", ["Central tendency", "Dispersion", "Skewness"])

            if st.button("Submit Streak"):
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

            # Q1
            responses["Q1_num"] = st.number_input("Q1: Mean of X1")
            responses["Q1_txt"] = st.text_area("Explain mean (Q1)")

            # Q2
            responses["Q2_num"] = st.number_input("Q2: SD of X3")
            responses["Q2_txt"] = st.text_area("Explain SD (Q2)")

            # Q3
            responses["Q3_txt"] = st.text_area("Q3: Which variable is most volatile? Why?")

            # Q4
            responses["Q4"] = st.radio("Q4: CV measures:", ["Central tendency", "Dispersion", "Skewness"])

            if st.button("Submit Quiz"):

                results = []
                total = 0

                # ----------------------------
                # CORRECT VALUES
                # ----------------------------
                mean_x1 = df["X1"].mean()
                sd_x3 = df["X3"].std()
                cv = df.std() / df.mean()
                most_vol = cv.idxmax()

                # ----------------------------
                # Q1
                # ----------------------------
                q1_score = 0
                feedback = ""

                if abs(responses["Q1_num"] - mean_x1) < 0.5:
                    q1_score += 0.5
                else:
                    feedback += f"Numeric wrong. Correct ≈ {round(mean_x1,2)}. "

                if "average" in responses["Q1_txt"].lower():
                    q1_score += 0.5
                else:
                    feedback += "Interpretation weak (mean = average)."

                total += q1_score
                results.append(("Q1", q1_score, feedback))

                # ----------------------------
                # Q2
                # ----------------------------
                q2_score = 0
                feedback = ""

                if abs(responses["Q2_num"] - sd_x3) < 0.5:
                    q2_score += 0.5
                else:
                    feedback += f"Numeric wrong. Correct ≈ {round(sd_x3,2)}. "

                if "spread" in responses["Q2_txt"].lower():
                    q2_score += 0.5
                else:
                    feedback += "Interpretation weak (SD = spread)."

                total += q2_score
                results.append(("Q2", q2_score, feedback))

                # ----------------------------
                # Q3
                # ----------------------------
                q3_score = 0
                feedback = ""

                if most_vol.lower() in responses["Q3_txt"].lower():
                    q3_score += 1
                else:
                    feedback += f"Wrong. Most volatile = {most_vol}"

                total += q3_score
                results.append(("Q3", q3_score, feedback))

                # ----------------------------
                # Q4
                # ----------------------------
                q4_score = 1 if responses["Q4"] == "Dispersion" else 0
                feedback = "" if q4_score else "CV measures dispersion"

                total += q4_score
                results.append(("Q4", q4_score, feedback))

                # ----------------------------
                # DISPLAY RESULT
                # ----------------------------
                st.subheader("📊 Detailed Evaluation")

                for q, score, fb in results:
                    st.write(f"{q}: {score}/1")
                    if fb:
                        st.write(f"🔴 {fb}")
                    else:
                        st.write("✅ Correct")

                max_marks = 4
                percent = (total / max_marks) * 100

                st.subheader("Final Score")
                st.write(f"{total} / {max_marks} ({round(percent,2)}%)")

                if percent >= 80:
                    st.success("🎉 Proficiency Achieved")
                    st.balloons()
                else:
                    st.warning("Needs improvement")

# =====================================================
# INSTRUCTOR MODE
# =====================================================
elif mode == "Instructor":

    st.header("Instructor Dashboard")
    st.write("Upload student files here (next step)")

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
