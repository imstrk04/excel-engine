import pytest
import pandas as pd

from excel_engine.interpreter import PlanInterpreter
from excel_engine import llm_client

@pytest.fixture
def interpreter(monkeypatch):
    
    fake_data = {
        'Structured_Data': pd.DataFrame({
            'EmployeeID': [1, 2, 3, 4],
            'Department': ['IT', 'IT', 'Sales', 'Sales'],
            'Salary': [100000, 50000, 80000, 60000],
            'Age': [30, 25, 40, 35],
            'JoiningDate': pd.to_datetime(['2020-01-01', '2021-03-15', '2019-05-20', '2022-07-30'])
        }),
        'Sales_Data': pd.DataFrame({
            'EmployeeID': [1, 2, 3, 5],
            'Total_Sales': [150000, 200000, 100000, 50000]
        }),
        'Unstructured_Data': pd.DataFrame({
            'RecordID': [101, 102],
            'CustomerFeedback': ["I love this product!", "This is terrible."]
        })
    }

    def mock_read_excel(file_path, sheet_name = None):
        return fake_data

    monkeypatch.setattr("pandas.read_excel", mock_read_excel)

    interpreter = PlanInterpreter(file_path="fake/path.xlsx")

    yield interpreter

def test_filter_and_aggregate(interpreter):
    test_plan = {
        "target_sheet": "Structured_Data",
        "operations": [
            {
                "type": "FILTER",
                "conditions": [
                    { "column": "Department", "operator": "==", "value": "IT" }
                ]
            },
            {
                "type": "AGGREGATE",
                "aggregations": [
                    { "column": "Salary", "function": "average" }
                ]
            }
        ]
    }

    result = interpreter.execute_plan(test_plan)

    expected_result = {
        "average_of_Salary": 75000.0
    }
    
    assert result == expected_result

def test_math_operation(interpreter):
    test_plan = {
        "target_sheet": "Structured_Data",
        "operations": [
            {
                "type": "MATH",
                "new_column": "Bonus",
                "expression": {
                    "col1": "Salary",
                    "operator": "*",
                    "value": 0.1
                }
            }
        ]
    }
    
    result = interpreter.execute_plan(test_plan)
    
    assert "Bonus" in result[0]
    assert result[0]["Bonus"] == 10000.0
    assert result[1]["Bonus"] == 5000.0

def test_date_operation(interpreter):
    test_plan = {
        "target_sheet": "Structured_Data",
        "operations": [
            {
                "type": "DATE_OP",
                "new_column": "Join_Year",
                "source_column": "JoiningDate",
                "operation": "extract_year"
            }
        ]
    }
    
    result = interpreter.execute_plan(test_plan)

    assert "Join_Year" in result[0]
    assert result[0]["Join_Year"] == 2020
    assert result[1]["Join_Year"] == 2021

def test_pivot_operation(interpreter):
    test_plan = {
        "target_sheet": "Structured_Data",
        "operations": [
            {
                "type": "PIVOT",
                "index": "Department",
                "columns": "Age", 
                "values": "Salary",
                "agg_func": "average"
            }
        ]
    }
    
    result = interpreter.execute_plan(test_plan)

    it_row = [row for row in result if row["Department"] == "IT"][0]
    
    assert it_row["25"] == 50000.0
    assert it_row["30"] == 100000.0
    assert it_row["35"] is None

def test_join_operation(interpreter):
    test_plan = {
        "target_sheet": "Structured_Data", 
        "operations": [
            {
                "type": "JOIN",
                "left_sheet": "Structured_Data",
                "right_sheet": "Sales_Data",
                "join_type": "inner",
                "on_column": "EmployeeID"
            }
        ]
    }
    
    result = interpreter.execute_plan(test_plan)

    assert len(result) == 3 
    
    assert "Total_Sales" in result[0]
    assert result[0]["EmployeeID"] == 1
    assert result[0]["Total_Sales"] == 150000

def test_unstructured_operation(interpreter, monkeypatch):
    def mock_llm_text_response(prompt):
        if "I love this product!" in prompt:
            return "Positive"
        if "This is terrible." in prompt:
            return "Negative"
        return "ERROR"

    monkeypatch.setattr(llm_client, "get_llm_text_response", mock_llm_text_response)
    
    test_plan = {
        "target_sheet": "Unstructured_Data",
        "operations": [
            {
                "type": "UNSTRUCTURED_OP",
                "operation": "sentiment_analysis",
                "source_column": "CustomerFeedback",
                "new_column": "Sentiment"
            }
        ]
    }
    
    result = interpreter.execute_plan(test_plan)
    
    assert "Sentiment" in result[0]
    assert result[0]["Sentiment"] == "Positive"
    assert result[1]["Sentiment"] == "Negative"