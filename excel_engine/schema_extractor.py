import pandas as pd

def get_excel_schema(file_path):
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
