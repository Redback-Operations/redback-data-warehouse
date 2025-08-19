# Data Preprocessing Pipeline

## Overview

This project is a configurable data preprocessing pipeline designed to handle multiple data types including tabular data (CSV/JSON), images, and videos. The pipeline reads raw input data, applies various preprocessing steps as specified in a YAML configuration file (`config.yaml`), and outputs the cleaned and transformed data into organized output folders. for morE info about how the config.yaml file works see `CONFIG_DOCUMENTATION.md`

## Features

- **Tabular Data Preprocessing:**  
  - Handling missing values with global or column-specific fills  
  - Encoding categorical variables (one-hot or label encoding)  
  - Normalization (Min-Max or Standard scaling)  
  - Outlier removal (IQR or z-score methods)  
  - Cleaning string columns (trimming, lowercasing)  
  - Column filtering (keep/drop specified columns)  
  - Data type conversions  
  - Duplicate removal  
  - Column renaming  
  - Adding unique row IDs  

- **Image Preprocessing:**  
  - Grayscale conversion  
  - Normalization  
  - Resizing  

- **Video Preprocessing:**  
  - Frame extraction at specified intervals  
  - Frame resizing  

## How it Works

- Define preprocessing steps and file paths in `config.yaml`.  
- Run the pipeline script (`preprocess.py`), which:  
  - Loads the config file  
  - Processes tabular, image, and video data as specified  
  - Saves processed outputs to designated folders  
  - Logs processing details and saves metadata JSON for each run 

  **Folder Structure**

  project_root/
├── config.yaml                  # Config file
├── preprocess.py                # Main pipeline script to run preprocessing
├── utils/                       # Source code (tabular.py, images.py, videos.py)
├── app.py                       # Streamlit app for testing
│
├── data/                       # Raw input data (as referenced in config)
│   ├── images/                 # Raw images folder (for image preprocessing)
│   │   ├── img1.png
│   │   └── img2.jpg
│   ├── videos/                 # Raw videos folder
│   │   └── sample.mp4
│   └── sample.csv              # Raw tabular CSV file
│
├── output/                     # Processed output data (created by the pipeline)
│   ├── images/                 # Processed images saved here
│   ├── tabular/                # Processed CSVs saved here
│   └── video_frames/           # Extracted and resized video frames
│
├── requirements.txt            # Python dependencies for the project
└── CONFIG_DOCUMENTATION.md     # Documentation for config file usage
└── README.md                   # Project Documentation 



## Getting Started

1.  Install dependencies:

    pip install -r requirements.txt

2. Prepare your raw data inside the `data/` folder.

3. Customize your preprocessing pipeline via config.yaml.

4. Run the pipeline:

       python preprocess.py

5. Run for testing:
     
      streamlit run app.py