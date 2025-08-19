
# Configuration File (`config.yaml`) Documentation

This document explains each configuration option in your YAML file, its purpose, accepted values, and how it affects preprocessing.

---

## 1. Tabular Section

```yaml
tabular:
  path: data/sample.csv
  output_folder: output/tabular
  type: csv
  preprocessing:
    add_row_id: true
    categorical_encoding:
      columns: [gender, city]
      method: onehot
    cleaning:
      lowercase: true
      remove_special_chars: false
      trim_strings: true
    column_filtering:
      drop: []
      keep: [age, income, gender, city]
    drop_duplicates: true
    dtype_conversion:
      age: int
      gender: category
      income: float
    missing_values:
      columns:
        age: 30
        name: Unknown
      global_fill: null
    normalization:
      columns: [age, income]
      method: minmax
    outlier_removal:
      columns: [age, income]
      method: iqr
      threshold: 1.5
    remove_empty_columns: true
    rename_columns:
      oldName: new_name
      productID: product_id
```

### Explanation of Fields

- **`path`**  
  - *Type:* string  
  - *Description:* File path to your raw tabular dataset (CSV or JSON).  
  - *Example:* `"data/sample.csv"`  
  - *Notes:* Must exist and be readable.

- **`output_folder`**  
  - *Type:* string  
  - *Description:* Directory where the processed tabular output will be saved as CSV.  
  - *Example:* `"output/tabular"`  
  - *Notes:* Directory will be created if missing.

- **`type`**  
  - *Type:* string (`csv` or `json`)  
  - *Description:* Specifies the format of the input tabular file.  
  - *Example:* `"csv"`

---

### `preprocessing` options

Each key under `preprocessing` is an optional step. If omitted, that step is skipped.

#### `add_row_id`  
- *Type:* boolean  
- *Description:* Adds a unique row ID column named `row_id` at the beginning of the DataFrame.

#### `categorical_encoding`  
- *Type:* dict  
- *Fields:*  
  - `columns` (list of strings): Columns to encode.  
  - `method` (string): Encoding method. Supported:  
    - `"onehot"` — creates one-hot encoded dummy variables.  
    - `"label"` — converts categories to integer labels.  
- *Notes:* Apply after filtering and cleaning.

#### `cleaning`  
- *Type:* dict  
- *Fields:*  
  - `lowercase` (bool): Convert string columns to lowercase.  
  - `remove_special_chars` (bool): (Not implemented yet — reserved for future) Remove special characters in strings.  
  - `trim_strings` (bool): Remove leading/trailing whitespace from string columns.

#### `column_filtering`  
- *Type:* dict  
- *Fields:*  
  - `keep` (list of strings): Keep only these columns (drop others). If specified, overrides `drop`.  
  - `drop` (list of strings): Drop these columns. Ignored if `keep` is present.  
- *Note:* Filtering should be done early for efficiency.

#### `drop_duplicates`  
- *Type:* boolean  
- *Description:* Remove exact duplicate rows.

#### `dtype_conversion`  
- *Type:* dict  
- *Fields:* key = column name, value = target data type (e.g., `int`, `float`, `category`, `str`).  
- *Example:*  
  ```yaml
  dtype_conversion:
    age: int
    income: float
  ```

#### `missing_values`  
- *Type:* dict  
- *Fields:*  
  - `columns`: dict mapping column names to fill values for missing entries.  
  - `global_fill`: single value to fill all missing values if specified (overrides column-specific fills). Use `null` to disable.  
- *Example:*  
  ```yaml
  missing_values:
    columns:
      age: 30
      name: Unknown
    global_fill: null
  ```

#### `normalization`  
- *Type:* dict  
- *Fields:*  
  - `columns` (list): Columns to normalize.  
  - `method` (string): Normalization method:  
    - `"minmax"` — scale values to [0,1] range.  
    - `"standard"` — zero mean, unit variance scaling.

#### `outlier_removal`  
- *Type:* dict  
- *Fields:*  
  - `columns` (list): Columns to check for outliers.  
  - `method` (string): Method to detect outliers:  
    - `"iqr"` — Interquartile Range method.  
    - `"zscore"` — Z-score thresholding.  
  - `threshold` (float): Threshold multiplier, e.g. 1.5 for IQR, or z-score limit.

#### `remove_empty_columns`  
- *Type:* boolean  
- *Description:* Remove columns that contain only missing values.

#### `rename_columns`  
- *Type:* dict  
- *Description:* Mapping from original column names to new names.  
- *Example:*  
  ```yaml
  rename_columns:
    oldName: new_name
    productID: product_id
  ```

---

## 2. Images Section

```yaml
images:
  path: temp_input/images
  output_folder: temp_output/images
  preprocessing:
    grayscale: true
    normalize: true
    resize: [128, 128]
```

- **`path`**  
  Folder containing input images.

- **`output_folder`**  
  Folder to save processed images.

- **`preprocessing`**  
  - `grayscale` (bool): Convert images to grayscale.  
  - `normalize` (bool): Normalize pixel values to [0,1].  
  - `resize` (list of two ints): Resize images to `[width, height]`.

---

## 3. Videos Section

```yaml
videos:
  path: data/videos/sample.mp4
  output_folder: output/video_frames
  preprocessing:
    extract_frames: 30
    resize_frames: [64, 64]
```

- **`path`**  
  Path to input video file.

- **`output_folder`**  
  Folder to save extracted and processed frames.

- **`preprocessing`**  
  - `extract_frames` (int): Number of frames to extract or interval.  
  - `resize_frames` (list of two ints): Resize extracted frames to `[width, height]`.

---

## How to use the config file

1. **Prepare your data and directory structure.**  
   Make sure your files and folders exist for the paths you set.

2. **Edit the YAML file** with the preprocessing steps you want for each data type.  
   - To skip a step, just remove or comment it out.  
   - Use boolean flags to toggle on/off steps.  
   - Provide lists for columns and mappings for renaming.

3. **Run the pipeline script.**  
   It will read your config and execute the steps in order.

4. **Check output folders** for processed files and logs.

5. **Review metadata JSON** for detailed information about each preprocessing step and statistics.

---
**FOLDER STRUCTURE**

project_root/
├── config.yaml                 # Config file
├── pipeline.py                 # Main pipeline script to run preprocessing
├── utils/                      # Source code (tabular.py, images.py, videos.py)
├── app.py                      # Streamlit app
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
