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

    st.header("👩‍🎓 Student Learning Agent")

    name = st.text_input("Enter Name")
    student_id = st.text_input("Enter Student ID")

    # ----------------------------
    # DATASET GENERATION
    # ----------------------------
    def generate_dataset(seed):
        np.random.seed(seed)
        return pd.DataFrame({
            "X1": np.random.normal(50, 10, 100),
            "X2": np.random.normal(60, 15, 100),
            "X3": np.random.normal(40, 25, 100),
        }).round(2)

    if st.button("Generate Dataset"):
        if student_id == "":
            st.warning("Enter Student ID")
        else:
            seed = sum(ord(c) for c in student_id)
            st.session_state["data"] = generate_dataset(seed)
            st.session_state["streak"] = 0
            st.session_state["current_q"] = None
            st.success("Dataset generated")

    # ----------------------------
    # MAIN FLOW
    # ----------------------------
    if "data" in st.session_state:

        df = st.session_state["data"]

        st.subheader("📊 Dataset Preview")
        st.dataframe(df.head())

        # Download full dataset
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Dataset", csv, f"{student_id}.csv")

        # =====================================================
        # STREAK MODE (NO REPETITION)
        # =====================================================
        st.subheader("🔥 Streak Mode (3 correct in a row)")

        if "streak" not in st.session_state:
            st.session_state["streak"] = 0

        # Initialize session variables safely
        if "streak" not in st.session_state:
            st.session_state["streak"] = 0

        if "current_q" not in st.session_state:
            st.session_state["current_q"] = np.random.choice(["mean", "sd", "cv"])
            st.session_state["current_q"] = np.random.choice(["mean", "sd", "cv"])

        qtype = st.session_state["current_q"]

        st.write(f"Current Streak: {st.session_state['streak']} / 3")

        if qtype == "mean":
            ans = st.number_input("Compute mean of X1", key="streak")

        elif qtype == "sd":
            ans = st.number_input("Compute SD of X3", key="streak")

        else:
            ans = st.radio("CV measures:", ["Central tendency", "Dispersion", "Skewness"], key="streak")

        if st.button("Submit Streak Answer"):

            if qtype == "mean":
                correct = df["X1"].mean()

                if abs(ans - correct) < 0.5:
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"""
Incorrect  

Correct ≈ {round(correct,2)}  

Mean = sum of values / number of observations  
Likely mistake: calculation or partial data usage
""")
                    st.session_state["streak"] = 0

            elif qtype == "sd":
                correct = df["X3"].std()

                if abs(ans - correct) < 0.5:
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error(f"""
Incorrect  

Correct ≈ {round(correct,2)}  

SD measures spread around mean  
Likely mistake: confusion with variance or wrong formula
""")
                    st.session_state["streak"] = 0

            else:
                if ans == "Dispersion":
                    st.success("Correct")
                    st.session_state["streak"] += 1
                else:
                    st.error("""
Incorrect  

CV = SD / Mean → measures dispersion  
Likely mistake: confusing with mean or skewness
""")
                    st.session_state["streak"] = 0

            # change question AFTER submission
            st.session_state["current_q"] = np.random.choice(["mean", "sd", "cv"])

        # =====================================================
        # FULL QUIZ (AUTO-GENERATED)
        # =====================================================
        if st.session_state["streak"] >= 3:

            st.success("🎉 Quiz Unlocked")

            st.subheader("🧪 Smart Quiz")

            questions = [
                {
                    "type": "numeric",
                    "q": "Compute mean of X2",
                    "answer": df["X2"].mean(),
                    "concept": "Mean represents average"
                },
                {
                    "type": "numeric",
                    "q": "Compute SD of X1",
                    "answer": df["X1"].std(),
                    "concept": "SD measures variability"
                },
                {
                    "type": "interpret",
                    "q": "Which variable is most volatile and why?",
                    "answer": (df.std()/df.mean()).idxmax(),
                    "concept": "Volatility via coefficient of variation"
                },
                {
                    "type": "mcq",
                    "q": "Coefficient of variation measures:",
                    "options": ["Central tendency", "Dispersion", "Shape"],
                    "answer": "Dispersion",
                    "concept": "CV = SD / Mean"
                }
            ]

            responses = []
            total = 0

            for i, q in enumerate(questions):

                st.markdown(f"### Q{i+1}: {q['q']}")

                if q["type"] == "numeric":
                    resp = st.number_input("Answer", key=f"q{i}")
                elif q["type"] == "interpret":
                    resp = st.text_area("Explain", key=f"q{i}")
                else:
                    resp = st.radio("Choose", q["options"], key=f"q{i}")

                responses.append(resp)

            if st.button("Submit Quiz"):

                st.subheader("📊 Detailed Feedback")

                for i, q in enumerate(questions):

                    if q["type"] == "numeric":

                        score = 0
                        fb = ""

                        if abs(responses[i] - q["answer"]) < 0.5:
                            score += 0.5
                        else:
                            fb += f"Correct ≈ {round(q['answer'],2)}. "

                        if "average" in str(responses[i]).lower():
                            score += 0.5
                        else:
                            fb += "Concept missing (mean/SD interpretation)."

                    elif q["type"] == "interpret":

                        score = 1 if q["answer"].lower() in responses[i].lower() else 0
                        fb = "" if score else f"Correct: {q['answer']}"

                    else:
                        score = 1 if responses[i] == q["answer"] else 0
                        fb = "" if score else "Correct answer: Dispersion"

                    total += score

                    st.write(f"Q{i+1}: {score}/1")
                    st.write("✅ Correct" if score == 1 else f"🔴 {fb}")

                percent = (total / len(questions)) * 100

                st.subheader("Final Score")
                st.write(f"{total}/{len(questions)} ({round(percent,2)}%)")

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
    st.write("Next step: upload and evaluate student files")
