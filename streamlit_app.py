import streamlit as st
import pandas as pd
import numpy as np
from hashlib import md5
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

st.title("📊 Business Analytics LMS - Pilot")

uploaded_files = st.file_uploader(
    "Upload student Excel files",
    accept_multiple_files=True
)

results = []
texts = []
names = []

def compute_answers(df):
    return {
        "mean": df.mean(),
        "std": df.std(),
        "cv": df.std() / df.mean()
    }

def hash_dataset(df):
    return md5(df.to_csv().encode()).hexdigest()

if uploaded_files:

    dataset_hashes = {}

    for file in uploaded_files:
        try:
            df = pd.read_excel(file, sheet_name="DATA")

            name = file.name
            names.append(name)

            correct = compute_answers(df)

            student_df = pd.read_excel(file, sheet_name="CALCULATIONS")
            text_df = pd.read_excel(file, sheet_name="INTERPRETATION")

            backup_df = pd.read_excel(file, sheet_name="BACKUP")

            backup_present = not backup_df.empty

            if not backup_present:
                score = 0
                remark = "No backup"
            else:
                score = 0

                # Numerical check (simplified)
                if np.isclose(student_df.iloc[0,0], correct["mean"].iloc[0]):
                    score += 0.5

                # Interpretation check
                text = str(text_df.iloc[0,0])
                texts.append(text)

                if "volatile" in text.lower():
                    score += 0.5

                remark = "Checked"

            # Dataset hash
            d_hash = hash_dataset(df)

            if d_hash in dataset_hashes:
                flag = "⚠️ Same dataset"
            else:
                dataset_hashes[d_hash] = name
                flag = ""

            results.append({
                "Student": name,
                "Score": score,
                "Backup": backup_present,
                "Flag": flag,
                "Remark": remark
            })

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")

    result_df = pd.DataFrame(results)
    st.dataframe(result_df)

    # Text similarity check
    if len(texts) > 1:
        vec = TfidfVectorizer().fit_transform(texts)
        sim = cosine_similarity(vec)

        st.subheader("🧠 Plagiarism Similarity Matrix")
        st.write(pd.DataFrame(sim, index=names, columns=names))
