import pandas as pd
import yaml
import os
import logging
from io import StringIO
from datetime import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder


with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

log = StringIO()

sh = logging.StreamHandler(log)
sh.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(sh)

#defining the pipeline procedure
class pipeline:
    def __init__(self, config):
        self.config = config
        self.scale = StandardScaler()
        self.le = LabelEncoder()

    def file_type(self, file_name):
        file = self.config["tabular"].get("file_type", "csv").lower()

        if file == "csv":
            df = pd.read_csv(file_name)
            logger.info(f"loaded the inputed CSV file {file_name}")
        elif file =="json":
            df = pd.read_json(file_name)
            logger.info(f"loaded the inputed JSON file {file_name}")
        else:
            raise ValueError(f"File type {file} not supported")
        return df
    
    def cleaning(self, df):
        cleaning = self.config['tabular']['preprocessing']['cleaning']

        #column filtering or dropping
        drop = cleaning.get("drop_columns", [])
        if drop:
            df.drop(columns=drop, errors="ignore", inplace=True)
            logger.info(f"Dropped the following columns: {drop}")

        
        #drop missing values
        drop_nan = cleaning.get("dropna", False)
        if drop_nan:
            df.dropna(inplace=True)
            logger.info("Dropped rows with missing values")


        #drop duplicate rows
        drop_dup = cleaning.get("drop_duplicates", False)
        if drop_dup:
            df.drop_duplicates(inplace=True)
            logger.info("Dropped duplicated rows")


        #renaming columns
        rename_dict = cleaning.get("rename_columns", {})
        if rename_dict:
            df.rename(columns=rename_dict, inplace=True)
            logger.info(f"Renamed the following columns: {rename_dict}")

        return df
    
    def transformation(self, df):
        transformation = self.config["tabular"]["preprocessing"]["transformation"]

        #encoding with Label encoder
        encode = transformation.get("categorical_encoding", {}).get("columns", [])
        for col in encode:
            df[col] = self.le.fit_transform(df[col].astype(str))
        logger.info(f"encoded these columns: {encode}")


        #filling missing values in columns
        fillna = transformation.get('fillna', {}).get("columns") or {}
        for col, method in fillna.items():
            if method == "mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif method == "median":
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(method, inplace=True)
            logger.info(f"Filled null values in {col} using {method}")

        
        #Normalizing numeric columns
        norm = transformation.get('normalize', {}).get("columns", [])
        if norm:
            df[norm] = self.scale.fit_transform(df[norm])
            logger.info(f"Normalized the following columns: {norm}")

        return df
    
    def validation(self, df):
        validation = self.config["tabular"]["preprocessing"]["validation"]

        #validating data types
        for cols in validation.get("dtype_conversion", []):
            for col, dtype in cols.items():
                try:
                    if dtype == "int":
                        df[col] = df[col].astype(int)
                    elif dtype == "float":
                        df[col] = df[col].astype(float)
                    elif dtype == "str":
                        df[col] = df[col].astype(str)
                    elif dtype == "datetime":
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                    logger.info(f"Converted {col} to {dtype}")
                except Exception as e:
                    logger.warning(f'Could not convert {col} to {dtype}')

        return df
    
    
    def save(self, df, input_file, output_dir="cleaned_files"):
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.basename(input_file)
        name, end = os.path.splitext(base)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"processed_{name}{timestamp}{end}")

                                   
        if end == ".csv":
            df.to_csv(output_file, index=False)
        elif end == ".json":
            df.to_json(output_file, orient="records")
        else:
            raise ValueError("Output file must be csv or json")
        logger.info(f"Saved file to {output_file}")

        return output_file
    

    def run(self, input_file):
        df = self.file_type(input_file)
        df = self.cleaning(df)
        df = self.transformation(df)
        df = self.validation(df)
        output_file = self.save(df, input_file)

        logs = log.getvalue()

        return output_file, logs