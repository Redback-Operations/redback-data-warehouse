import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
from scipy.stats import zscore
import os

# ------------------------------
# Missing Values
# ------------------------------
def handle_missing_values(df, missing_cfg, logger=None):
    meta = {'missing_values_filled': 0}
    if logger:
        logger.info("Handling missing values")

    before_na = df.isna().sum().sum()

    if 'global_fill' in missing_cfg and missing_cfg['global_fill'] is not None:
        df = df.fillna(missing_cfg['global_fill'])
        if logger:
            logger.debug(f"Filled all missing values with: {missing_cfg['global_fill']}")

    if 'columns' in missing_cfg:
        for col, val in missing_cfg['columns'].items():
            if col in df.columns:
                df[col] = df[col].fillna(val)
                if logger:
                    logger.debug(f"Filled missing values in column '{col}' with: {val}")

    after_na = df.isna().sum().sum()
    meta['missing_values_filled'] = before_na - after_na
    return df, meta

# ------------------------------
# Normalization
# ------------------------------
def normalize_columns(df, norm_cfg, logger=None):
    meta = {}
    method = norm_cfg.get('method', 'minmax')
    cols = norm_cfg.get('columns', [])

    if not cols:
        if logger:
            logger.info("No columns specified for normalization; skipping")
        return df, meta

    if logger:
        logger.info(f"Normalizing columns {cols} using method '{method}'")

    if method == 'minmax':
        scaler = MinMaxScaler()
    elif method == 'standard':
        scaler = StandardScaler()
    else:
        if logger:
            logger.warning(f"Unknown normalization method '{method}'; skipping normalization")
        return df, meta

    df[cols] = scaler.fit_transform(df[cols])
    meta['normalized_columns'] = cols
    meta['normalization_method'] = method
    return df, meta

# ------------------------------
# Encoding
# ------------------------------
def encode_categorical(df, encode_cfg, logger=None):
    meta = {}
    method = encode_cfg.get('method', 'onehot')
    cols = encode_cfg.get('columns', [])

    if logger:
        logger.info(f"Encoding categorical columns {cols} using method '{method}'")

    if method == 'label':
        for col in cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                if logger:
                    logger.debug(f"Label encoded column '{col}'")
        meta['encoded_columns'] = cols
        meta['encoding_method'] = 'label'

    elif method == 'onehot':
        existing_cols = [c for c in cols if c in df.columns]
        df = pd.get_dummies(df, columns=existing_cols)
        meta['encoded_columns'] = existing_cols
        meta['encoding_method'] = 'onehot'
        if logger:
            logger.debug(f"One-hot encoded columns {existing_cols}")

    else:
        if logger:
            logger.warning(f"Unknown encoding method '{method}'; skipping encoding")

    return df, meta

# ------------------------------
# Outlier Removal
# ------------------------------
def remove_outliers(df, outlier_cfg, logger=None):
    meta = {'outliers_removed': 0}
    method = outlier_cfg.get('method', 'iqr')
    cols = outlier_cfg.get('columns', [])
    threshold = outlier_cfg.get('threshold', 1.5)

    if logger:
        logger.info(f"Removing outliers using method '{method}' on columns {cols} with threshold {threshold}")

    before_rows = df.shape[0]

    if method == 'iqr':
        for col in cols:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

    elif method == 'zscore':
        for col in cols:
            if col in df.columns:
                z_scores = np.abs(zscore(df[col]))
                df = df[z_scores < threshold]

    else:
        if logger:
            logger.warning(f"Unknown outlier removal method '{method}'; skipping")

    after_rows = df.shape[0]
    meta['outliers_removed'] = before_rows - after_rows
    return df, meta

# ------------------------------
# Cleaning
# ------------------------------
def clean_data(df, cleaning_cfg, logger=None):
    meta = {}
    if logger:
        logger.info("Cleaning data")

    if cleaning_cfg.get('trim_strings', False):
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        meta['trim_strings'] = True
        if logger:
            logger.debug("Trimmed strings in dataframe")

    if cleaning_cfg.get('lowercase', False):
        df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        meta['lowercase'] = True
        if logger:
            logger.debug("Lowercased strings in dataframe")

    return df, meta

# ------------------------------
# Column Filtering
# ------------------------------
def filter_columns(df, filter_cfg, logger=None):
    meta = {}
    if 'keep' in filter_cfg and filter_cfg['keep']:
        df = df.loc[:, filter_cfg['keep']]
        meta['columns_kept'] = filter_cfg['keep']
        if logger:
            logger.info(f"Filtered columns, keeping only: {filter_cfg['keep']}")
    elif 'drop' in filter_cfg and filter_cfg['drop']:
        df = df.drop(columns=filter_cfg['drop'], errors='ignore')
        meta['columns_dropped'] = filter_cfg['drop']
        if logger:
            logger.info(f"Dropped columns: {filter_cfg['drop']}")
    return df, meta

# ------------------------------
# Dtype Conversion
# ------------------------------
def convert_dtypes(df, dtype_cfg, logger=None):
    meta = {'dtype_conversions': {}}
    for col, dtype in dtype_cfg.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(dtype)
                meta['dtype_conversions'][col] = dtype
                if logger:
                    logger.debug(f"Converted column '{col}' to dtype '{dtype}'")
            except Exception as e:
                warn_msg = f"Warning: could not convert column {col} to {dtype}: {e}"
                if logger:
                    logger.warning(warn_msg)
                else:
                    print(warn_msg)
    return df, meta

# ------------------------------
# Remove Empty Columns
# ------------------------------
def remove_empty_columns(df, logger=None):
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    if empty_cols:
        df = df.drop(columns=empty_cols)
        if logger:
            logger.info(f"Removed empty columns: {empty_cols}")
    return df, {'empty_columns_removed': empty_cols}

# ------------------------------
# Add Row IDs
# ------------------------------
def add_row_ids(df, logger=None):
    df.insert(0, 'row_id', range(1, len(df) + 1))
    if logger:
        logger.info("Added unique row_id column")
    return df, {'row_id_added': True}

# ------------------------------
# Drop Duplicates
# ------------------------------
def drop_duplicates(df, drop_cfg=True, logger=None):
    meta = {'duplicates_removed': 0}
    if drop_cfg:
        before_rows = df.shape[0]
        df = df.drop_duplicates()
        after_rows = df.shape[0]
        meta['duplicates_removed'] = before_rows - after_rows
        if logger:
            logger.info(f"Removed {meta['duplicates_removed']} duplicate rows")
    return df, meta

# ------------------------------
# Rename Columns
# ------------------------------
def rename_columns(df, rename_cfg, logger=None):
    meta = {}
    if rename_cfg:
        df = df.rename(columns=rename_cfg)
        meta['columns_renamed'] = rename_cfg
        if logger:
            logger.info(f"Renamed columns: {rename_cfg}")
    return df, meta

# ------------------------------
# Main Preprocess
# ------------------------------
def preprocess_tabular(df, cfg, logger=None):
    metadata = []

    def record_step(name, meta):
        metadata.append({"step": name, **meta})

    if cfg.get('remove_empty_columns', False):
        df, meta = remove_empty_columns(df, logger=logger)
        record_step('remove_empty_columns', meta)

    if cfg.get('add_row_id', False):
        df, meta = add_row_ids(df, logger=logger)
        record_step('add_row_id', meta)

    if cfg.get('drop_duplicates', False):
        df, meta = drop_duplicates(df, logger=logger)
        record_step('drop_duplicates', meta)

    if 'rename_columns' in cfg:
        df, meta = rename_columns(df, cfg['rename_columns'], logger=logger)
        record_step('rename_columns', meta)

    if 'missing_values' in cfg:
        df, meta = handle_missing_values(df, cfg['missing_values'], logger=logger)
        record_step('handle_missing_values', meta)

    if 'normalization' in cfg:
        df, meta = normalize_columns(df, cfg['normalization'], logger=logger)
        record_step('normalize_columns', meta)

    if 'categorical_encoding' in cfg:
        df, meta = encode_categorical(df, cfg['categorical_encoding'], logger=logger)
        record_step('encode_categorical', meta)

    if 'outlier_removal' in cfg:
        df, meta = remove_outliers(df, cfg['outlier_removal'], logger=logger)
        record_step('remove_outliers', meta)

    if 'cleaning' in cfg:
        df, meta = clean_data(df, cfg['cleaning'], logger=logger)
        record_step('clean_data', meta)

    if 'column_filtering' in cfg:
        df, meta = filter_columns(df, cfg['column_filtering'], logger=logger)
        record_step('filter_columns', meta)

    if 'dtype_conversion' in cfg:
        df, meta = convert_dtypes(df, cfg['dtype_conversion'], logger=logger)
        record_step('convert_dtypes', meta)

    return df, metadata

# ------------------------------
# Save Tabular Output
# ------------------------------
def save_processed_tabular(df, output_folder, logger=None):
    os.makedirs(os.path.dirname(output_folder), exist_ok=True)
    df.to_csv(output_folder, index=False)
    if logger:
        logger.info(f"Saved processed tabular data to {output_folder}")
