# CONFIGURABLE PREPROCESSING PIPELINE

This readme explains all there is in the configurable data preprocessing pipeline and how it works

# cleaned_files
This folder is where all the cleaned and processed files will be stored

# temp
This folder is a temporary folder created by streamlit to run the uploaded file, its also where the original uploaded file will be stored so there will be reference to cleaned files

# config.yaml
This is where configuration for the pipeline will be made, For more info check `READCONFIG.md`.

# requirements.txt
all intalled dependencies are stored here

# stream.py
Contains the interface to upload the file and streamlit script to run the pipeline running as `streamlit run stream.py`

# tabular_pipeline.py
This is the main pipeline where the preprocessing steps will be done

The pipeline uses these imports:
`pandas`: For data manipulation
`yaml`: loads the `config.yaml` automatically
`os`: Handles file paths and directory
`logging`: logs actions taken as in the pipeline
`StringIO`: Stores logs in memory instead of printing
`datetime`: generates timestamped file names
`sklearn.preprocessing`: standardscaler; for the data normalization. `LabelEncoder; for encoding the categorical column to integer

All these libraries contribute to the pipeline structure and does what its suppose to do in accordance to the preset `config.yaml`

These pipeline is backed up with a streamlit app which acts as the user interface and where files will be uploaded

to run the pipeline

steps to run the pipeline:
# 1. setup the config file using the `READCONFIG.md` as guide
# 2. run `streamlit run stream.py` for the upload interface
# 3. Upload the file check the logging steps in that same interface to see the progress of the pipeline
# 4. once done, the preprocessed file get stored automatically in the `cleaned_files` directory