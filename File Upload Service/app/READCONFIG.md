# config.yaml

This documentation entails what each line of the `config.yaml` file for the configurable-data-preprocessing-pipeline means and how it should be written to avoid errors

# tabular
This is the main title or header of the config, which all preprocessing style and steps are under.

# file_type
This asks the question about what type of file it is, for now this yaml file `config.yaml` accepts just `csv or json` file to be preprocessed, any other file will lead to an error.

# preprocessing
Under this is where all preprocessing options are stated and it is broken down into cleaning, transformation and validation as subsections.

# cleaning
Under cleaning we have drop_columns, dropna, drop_duplicates and rename_column steps which would all be explained below

# drop_columns:
This section under `cleaning` entails which of the column the user will like to drop or not include in the uploaded dataframe as output. note: each columns should be written in accordance to how it looks in the dataframe and it should be written with a dash in front (-) eg `- product`

# dropna:
This section still under `cleaning`, asks if the user wants to drop null or empty values its either a `true or false` response.

# drop_duplicates
Still under `cleaning`. it drops duplicate rows to reduice noise in a dataset, its either a `true or false` response.

# rename_columns
This option has to do with changing column names, oldname comes first then new name comes for example `sales: revenue`.

# transformation
This is the next section under `preprocessing` it contains `categorical_encoding` and `fillna` as subsections, and these will be explained below

# categorical_encoding
This option allows the user encode categorical or words into numbers or numeric values, how to use it: you write down the column you want to encode like this `- column1` and the pipeline changes words into numbers.

# fillna
This acts like the opposite of the `dropna` option, because you either want to drop none existing columns or fill them up with values, this `fillna` option allows you fill them up with either the column mean, median, mode or enter the value you like and it is written like `column: mean`.

# normalize
Currently we use StandardScaler to normalize data, its kept as list sinse we are not normalizing any columns but when normalization is to be done, its writen as `- column` under the columns section in the normalize.

# validation
# dtype_conversion
This contains just data type changing like changing numerical columns to float or integer, changing datetime to datetime



# below is the format for the `config.yaml` file
```
tabular:
  file_type: #csv or json
  preprocessing:
    cleaning:
      drop_columns:
        # - column1
        # - column2
      dropna: true
      drop_duplicates: true
      rename_columns:
        # old_name1: new_name1
        # old_name2: new_name2
    transformation:
      categorical_encoding:
        columns:
          # - column 1
          # - column 2
      fillna:
        columns:
          # column1: mean
          # column2: median
          # column3: mode
          # column4: value
      normalize:
        columns: []
    validation:
      dtype_conversion:
        # - date: datetime

```


NOTE: Once all configuration have been made the pipeline will process correctly with no errors.