import pandas as pd
import numpy as np
import re

# Regular expression patterns which will used for detecting column with some kind of date
# (datetime, date, time)
regular_expression_for_date = r'[\d]{4}-[\d]{2}-[\d]{2}\s00:00:00'
regular_expression_for_time = r'[\d]{1,2}:[\d]{1,2}'
regular_expression_for_datetime = r'[\d]{4}-[\d]{2}-[\d]{2}\s[\d]{2}:[\d]{2}:[\d]{2}'

threshold_percentage_of_missing_values = 0.01


# Class which contain all properties for analyzed object from file
class AnalyzedObject:

    def __init__(self):
        self.dataset                           = None
        self.column_names_input                = []
        self.column_names_output               = []
        self.column_types                      = {}
        self.lines_for_training_count          = 0
        self.lines_to_predict_count            = 0
        self.lines_to_skip_count               = 0
        self.errors_info                       = {}
        self.warning_info                      = {}
        self.lines_to_predict_indexes_list     = []
        self.lines_to_skip_indexes_list        = []

    def add_error_info_for_column(self, column, error_message):
        if column not in self.errors_info:
            self.errors_info[column] = error_message
        else:
            self.errors_info[column] += error_message

    def add_warning_info_for_column(self, column, warning_message):
        if column not in self.warning_info:
            self.warning_info[column] = warning_message
        else:
            self.warning_info[column] += warning_message


# Check count of missing values. In output columns should be the same number of missing values
def check_missing_data_count(analyzer_object, columns_with_missing_data_dict):
    # Count unique numbers
    unique_count = set(columns_with_missing_data_dict.values())

    if unique_count == 1:
        return list(columns_with_missing_data_dict.keys())

    # Check columns with less missing values and write warning
    else:
        max_num = max(columns_with_missing_data_dict.values())
        for column in columns_with_missing_data_dict:
            if columns_with_missing_data_dict[column] < max_num:
                analyzer_object.add_warning_info_for_column(column, "In this column are less values than in another "
                                                                    "output columns\n")

        return list(columns_with_missing_data_dict.keys())


# Check type of columns data with regular expression ( Date, DateTime, Time )
def check_date_type(column_from_dataset, reg_pattern):
    return all(len(re.findall(reg_pattern, str(data))) == 1 for data in column_from_dataset)


# Check splitter in column (Comma, DotsComma, just words)
def check_tags(analyzer_object, column_from_dataset):

    count_commas = 0
    count_dots_comma = 0

    for data in column_from_dataset:
        count_dots_comma += str(data).count(';')
        count_commas += str(data).count(',')

    # Choose more common tags splitter
    if count_commas == 0 and count_dots_comma == 0:
        return 'TAGS'

    elif count_dots_comma > count_commas:
        if count_dots_comma == len(column_from_dataset):
            return 'TAGS_DOTCOMMA'
        else:
            analyzer_object.add_warning_info_for_column(column_from_dataset.name, 'In column are different split style\n')
            return 'TAGS_DOTCOMMA'

    elif count_commas > count_dots_comma:
        if count_commas == len(column_from_dataset):
            return 'TAGS_COMMA'
        else:
            analyzer_object.add_warning_info_for_column(column_from_dataset.name, 'In column are different split style\n')
            return 'TAGS_COMMA'


# Using this function to check most common type of data in column with different data types
def check_type_for_column_with_mixed_data(analyzer_object, column_from_dataset):

    # Using list comprehension to create two list with indexes (for numbers and for string)
    count_numbers = [index for index in range(len(column_from_dataset)) if re.findall('[0-9]', str(column_from_dataset[index]))]
    count_string = [index for index in range(len(column_from_dataset)) if re.findall('[A-Za-z]', str(column_from_dataset[index]))]

    # Detect more common type of data and return this
    if len(count_string) > len(count_numbers):
        # Check if all data is string values.
        if len(count_string) == len(column_from_dataset):
            return 'TAGS'
        else:
            analyzer_object.add_warning_info_for_column(column_from_dataset.name, 'This column is string but have some '
                                                                                  'numeric data\n')
            analyzer_object.lines_to_skip_indexes_list += count_numbers
            return 'TAGS'

    elif len(count_string) < len(count_numbers):
        analyzer_object.add_warning_info_for_column(column_from_dataset.name, 'This column is numeric but have some '
                                                                              'string data\n')
        analyzer_object.lines_to_skip_indexes_list += count_string
        return 'NUMERIC'


def analyse_source_data_find_input_output(filename_with_data):

    analyzed_object_from_file = AnalyzedObject()
    dataframe_from_file = None
    columns_type = {}

    # Check format of input file and read file with pandas
    if filename_with_data.endswith('.csv'):
        dataframe_from_file = pd.read_csv(filename_with_data, sep='\t', engine='python')

    elif filename_with_data.endswith('.xls') or filename_with_data.endswith('.xlsx'):
        dataframe_from_file = pd.read_excel(filename_with_data)

    number_of_rows_in_dataset = len(dataframe_from_file)

    # Check size of dataframe. If size == 0 return message with error
    if number_of_rows_in_dataset == 0 or dataframe_from_file is None:
        analyzed_object_from_file.add_error_info_for_column('Dataset', 'Dataset is empty or bad file format\n')
        return analyzed_object_from_file

    # Search empty column and delete from dataset. Write info to warnings
    empty_columns = dataframe_from_file.columns[dataframe_from_file.isna().all()].tolist()
    if empty_columns:
        for column in empty_columns:
            analyzed_object_from_file.add_warning_info_for_column(column, "All data is missing in column\n")
            columns_type[column] = 'EMPTY'

    dataframe_from_file = dataframe_from_file.drop(columns=empty_columns)

    # Create list of column names for columns without data in some rows
    list_of_columns_with_missing_values = dataframe_from_file.columns[dataframe_from_file.isna().any()].tolist()

    # Search to_predict_columns
    columns_with_missing_data_dict = {}
    for column in dataframe_from_file.columns:
        number_of_absent_rows_for_column = dataframe_from_file[column].isna().sum()

        if number_of_absent_rows_for_column > number_of_rows_in_dataset * threshold_percentage_of_missing_values:
            columns_with_missing_data_dict[column] = number_of_absent_rows_for_column
            # Remove to_predict column from list with columns with missing data
            list_of_columns_with_missing_values.remove(column)

    # Check if output columns are found and save output column names to analyzed object
    if len(columns_with_missing_data_dict) > 0:
        analyzed_object_from_file.column_names_output = check_missing_data_count(analyzed_object_from_file,
                                                                                 columns_with_missing_data_dict)
    else:
        analyzed_object_from_file.add_error_info_for_column('DATASET', 'Columns to predict not found\n')

    # Write warning message for all columns if column have nan and column not to_predict
    if list_of_columns_with_missing_values:
        for column in list_of_columns_with_missing_values:
            analyzed_object_from_file.add_warning_info_for_column(column, 'Have missing data in some rows\n')
    # Remove all rows with nan if nan not in to_predict column
    dataframe_from_file = dataframe_from_file.dropna(subset=list_of_columns_with_missing_values).reset_index()
    dataframe_from_file = dataframe_from_file.drop(columns='index')

    # For each column save their data type
    for column in dataframe_from_file:
        if dataframe_from_file[column].dtype == np.float64 or dataframe_from_file[column].dtype == np.int64:
            # If in column just 2 different values then type of column is BINARY
            # If in columns with numbers are less than 20 unique values then type of column is OPTION
            if dataframe_from_file[column].nunique() == 2:
                columns_type[column] = 'BINARY'
            elif dataframe_from_file[column].nunique() < 20:
                columns_type[column] = 'OPTION'
            else:
                columns_type[column] = 'NUMERIC'

        elif check_date_type(dataframe_from_file[column], regular_expression_for_date):
            columns_type[column] = 'DATE'

        elif check_date_type(dataframe_from_file[column], regular_expression_for_datetime):
            columns_type[column] = 'DATETIME'

        elif check_date_type(dataframe_from_file[column], regular_expression_for_time):
            columns_type[column] = 'TIME'

        # In column with type object can be data with different types.
        elif dataframe_from_file[column].dtype == object:
            # Choose most common type
            if check_type_for_column_with_mixed_data(analyzed_object_from_file, dataframe_from_file[column]) == 'NUMERIC':
                dataframe_from_file[column] = pd.to_numeric(dataframe_from_file[column], errors='coerce')
                if dataframe_from_file[column].nunique() == 2:
                    columns_type[column] = 'BINARY'
                elif dataframe_from_file[column].nunique() < 20:
                    columns_type[column] = 'OPTION'
                else:
                    columns_type[column] = 'NUMERIC'
            elif check_type_for_column_with_mixed_data(analyzed_object_from_file, dataframe_from_file[column]) == 'TAGS':
                columns_type[column] = check_tags(analyzed_object_from_file, dataframe_from_file[column])

    # Save dataset properties to object
    analyzed_object_from_file.column_types = columns_type
    analyzed_object_from_file.column_names_input = dataframe_from_file.columns[dataframe_from_file.notna().all()].tolist()

    analyzed_object_from_file.dataset = dataframe_from_file.drop(analyzed_object_from_file.lines_to_skip_indexes_list).reset_index()
    analyzed_object_from_file.dataset = analyzed_object_from_file.dataset.drop(columns='index')

    analyzed_object_from_file.lines_to_skip_count = number_of_rows_in_dataset - len(analyzed_object_from_file.dataset)

    for row in range(len(analyzed_object_from_file.dataset)):
        if pd.isna(analyzed_object_from_file.dataset.iloc[row]).any():
            # Add index of row with missing value to list
            analyzed_object_from_file.lines_to_predict_indexes_list.append(row)
            analyzed_object_from_file.lines_to_predict_count += 1

        else:
            analyzed_object_from_file.lines_for_training_count += 1
    # analyzed_object_from_file.dataset.to_excel('fwef.xls')
    return analyzed_object_from_file


if __name__ == '__main__':
    A = analyse_source_data_find_input_output('test-2.xls')
    print('-------------------INPUT COLUMNS----------------------')
    print(A.column_names_input)
    print('-------------------OUTPUT COLUMNS----------------------')
    print(A.column_names_output)
    print('-------------------COLUMN TYPES------------------------')
    print(A.column_types)
    print('-------------------LINES FOR TRAINING----------------------')
    print(A.lines_for_training_count)
    print('-------------------LINES TO PREDICT----------------------')
    print(A.lines_to_predict_count)
    print('-------------------LINES TO SKIP----------------------')
    print(A.lines_to_skip_count)
    print('-------------------LINES TO PREDICT INDEXES----------------------')
    print(A.lines_to_predict_indexes_list)
    print('-------------------WARNINGS--------------------------')
    print(A.warning_info)
    print('-------------------ERRORS---------------------------')
    print(A.errors_info)