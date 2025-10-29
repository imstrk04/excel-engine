"""
The one and only job of this file is to read an Excel file and report its "shape." 
It needs to answer the question: "What sheets are in this file, and what columns are in each sheet?" 
This "shape" is called the schema.
"""

# imports
import pandas as pd
from typing import Dict, List # used for 'type hints'

def get_excel_schema(file_path: str) -> Dict[str, List[str]]:
    """
    Reads an excel file and returns a dictionary mapping
    sheet names to their column names.

    Args:
        file_path: The full path of .xlsx file.
    
    Returns:
        A dictionary where keys are sheet names and values are
        list of column names.
    """

    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names

    schema = {} # dictionary to store sheet name -> list of columns

    for sheet in sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, nrows=0) # nrows=0 because we dont need any data
        schema[sheet] = list(df.columns)
    
    return schema

if __name__ == "__main__":
    test_path = "data/synthetic_data.xlsx"
    try:
        file_schema = get_excel_schema(test_path)

        for sheet_name, columns in file_schema.items():
            print(f"Sheet Name:{sheet_name}")
            print(",".join(columns))
    except FileNotFoundError:
        print(f"File Not Found at {test_path}")
