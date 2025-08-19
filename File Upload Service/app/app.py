import streamlit as st
import yaml
import os
import subprocess
import pandas as pd
import json
import shutil
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Redback Preprocessing Tester", layout="centered")
st.title("🧹 Redback Data Preprocessing Test App")

# Unified uploader
uploaded_files = st.file_uploader(
    "📁 Upload Tabular (CSV/JSON), Images (PNG/JPG), or Video (MP4)",
    type=["csv", "json", "png", "jpg", "jpeg", "mp4"],
    accept_multiple_files=True
)

# Separate config uploader
config_file = st.file_uploader("📄 Upload YAML Config", type=["yaml", "yml"])

# Initialize containers
tabular_file = None
image_files = []
video_file = None

# Sort uploaded files
if uploaded_files:
    for file in uploaded_files:
        ext = file.name.lower().split('.')[-1]
        if ext in ["csv", "json"] and tabular_file is None:
            tabular_file = file
        elif ext in ["png", "jpg", "jpeg"]:
            image_files.append(file)
        elif ext == "mp4" and video_file is None:
            video_file = file

# Proceed if config is uploaded
if config_file:
    with st.spinner("Preparing files..."):
        # Save config
        config_path = "config.yaml"
        with open(config_path, "wb") as f:
            f.write(config_file.getvalue())

        # Load config
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Check required input folders exist, else error out
        # Tabular file handling
        if tabular_file and "tabular" in config:
            tabular_path = os.path.join("temp_input", tabular_file.name)
            if not os.path.isdir("temp_input"):
                st.error("Input folder 'temp_input' does not exist. Please create it manually.")
                st.stop()
            with open(tabular_path, "wb") as f:
                f.write(tabular_file.getvalue())
            config["tabular"]["path"] = tabular_path
            if "output_folder" not in config["tabular"]:
                st.error("Config 'tabular' section missing 'output_folder'.")
                st.stop()

        # Image files handling
        if image_files and "images" in config:
            img_dir = "temp_input/images"
            if not os.path.isdir(img_dir):
                st.error(f"Input images folder '{img_dir}' does not exist. Please create it manually.")
                st.stop()
            for img in image_files:
                with open(os.path.join(img_dir, img.name), "wb") as f:
                    f.write(img.getvalue())
            config["images"]["path"] = img_dir
            if "output_folder" not in config["images"]:
                st.error("Config 'images' section missing 'output_folder'.")
                st.stop()

        # Video file handling
        if video_file and "videos" in config:
            video_path = os.path.join("temp_input", video_file.name)
            if not os.path.isdir("temp_input"):
                st.error("Input folder 'temp_input' does not exist. Please create it manually.")
                st.stop()
            with open(video_path, "wb") as f:
                f.write(video_file.getvalue())
            config["videos"]["path"] = video_path
            if "output_folder" not in config["videos"]:
                st.error("Config 'videos' section missing 'output_folder'.")
                st.stop()

        # Save updated config
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        st.subheader("✅ Config Loaded")
        st.json(config)

    # Run preprocessing
    st.info("Running preprocessing pipeline...")
    with st.spinner("Processing..."):
        try:
            result = subprocess.run(["python", "preprocess.py"], capture_output=True, text=True)
            st.text(result.stdout)
            if result.stderr:
                st.error(result.stderr)
        except Exception as e:
            st.error(f"❌ Pipeline execution failed: {e}")
            st.stop()

    # Tabular preview
    tabular_out = os.path.join(config["tabular"]["output_folder"], "processed_tabular.csv")
    if os.path.exists(tabular_out):
        st.subheader("📈 Tabular Output Preview")
        df_out = pd.read_csv(tabular_out)
        st.dataframe(df_out.head())
    else:
        st.warning(f"Tabular output file not found: {tabular_out}")

    # Image preview
    img_out_dir = config["images"]["output_folder"]
    if os.path.exists(img_out_dir):
        img_files = sorted(os.listdir(img_out_dir))[:5]
        if img_files:
            st.subheader("🖼️ Processed Images Preview")
            for img_name in img_files:
                img_path = os.path.join(img_out_dir, img_name)
                st.image(Image.open(img_path), caption=img_name)
    else:
        st.warning(f"Image output folder not found: {img_out_dir}")

    # Video frame preview
    vid_out_dir = config["videos"]["output_folder"]
    if os.path.exists(vid_out_dir):
        frame_files = sorted(os.listdir(vid_out_dir))[:5]
        if frame_files:
            st.subheader("🎥 Processed Video Frames Preview")
            for frame_name in frame_files:
                frame_path = os.path.join(vid_out_dir, frame_name)
                st.image(Image.open(frame_path), caption=frame_name)
    else:
        st.warning(f"Video frames output folder not found: {vid_out_dir}")

    # Metadata display
    metadata_files = [f for f in os.listdir() if f.startswith("metadata_") and f.endswith(".json")]
    if metadata_files:
        latest_meta = sorted(metadata_files)[-1]
        with open(latest_meta, "r") as f:
            metadata = json.load(f)
        st.subheader("🧾 Metadata Summary")
        st.json(metadata)

    st.success("✅ Processing complete and preview displayed.")
