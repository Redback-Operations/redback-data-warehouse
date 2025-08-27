import streamlit as st
import os
import yaml
from tabular_pipeline import pipeline

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

pipe = pipeline(config)

st.title("Configurable Data Preprocessing Pipeline")

uploaded_file = st.file_uploader("Upload your file must be (CSV or JSON)", type=["csv", "json"])

if uploaded_file:
    file = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(file, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"Uploaded {uploaded_file.name}")
    
    
    if st.button("Preprocess Data"):
        try:
            output_file, logs = pipe.run(file)
            st.success(f"Preprocessing complete! Please check the 'cleaned_files' Folder in the directory.")
            st.text_area("Processing Logs", logs, height=300)
        except Exception as e:
            st.error(f"Error: {e}")
