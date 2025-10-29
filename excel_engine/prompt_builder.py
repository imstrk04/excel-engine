"""
The one and only job of this file is to assemble the complete, 
detailed prompt we'll send to the LLM. 
It takes the data schema and the user's query and wraps them in
a set of instructions that "teaches" the LLM how to create our JSON plan.
"""

from typing import Dict, List

OPERATION_PROMPT_GUIDELINES = """
You are a data analysis assistant. Your ONLY job is to convert a user's query into a structured JSON operation plan.
You MUST follow these rules:
- Only output the JSON plan. Do not add explanations or introductions.
- The plan is an array of operations. Operations are executed in order.
- Always use the exact column names provided in the schema.
- Pay attention to data types (e.g., 'Salary' is number, 'Department' is string).

Here are the allowed operations:

1. "FILTER"
   - Used for filtering rows based on conditions.
   - Example Query: "employees in IT with a salary over 50000"
   - JSON:
     {
       "operations": [
         {
           "type": "FILTER",
           "conditions": [
             { "column": "Department", "operator": "==", "value": "IT" },
             { "column": "Salary", "operator": ">", "value": 50000 }
           ]
         }
       ]
     }
   - Allowed operators: ==, !=, >, <, >=, <=

2. "AGGREGATE"
   - Used for calculations like average, sum, min, max, count.
   - Example Query: "what is the average salary and max age?"
   - JSON:
     {
       "operations": [
         {
           "type": "AGGREGATE",
           "aggregations": [
             { "column": "Salary", "function": "average" },
             { "column": "Age", "function": "max" }
           ]
         }
       ]
     }
   - Allowed functions: average, sum, min, max, count.
   - This operation is often preceded by a FILTER.

3. "MATH"
   - Used to create a new column by performing math on an existing one.
   - Example Query: "create a new column 'Bonus' that is Salary * 0.1"
   - JSON:
     {
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
   - Allowed operators: +, -, *, /

4. "DATE_OP"
   - Used to extract parts of a date.
   - Example Query: "extract the month from 'JoiningDate'"
   - JSON:
     {
       "operations": [
         {
           "type": "DATE_OP",
           "new_column": "JoiningMonth",
           "source_column": "JoiningDate",
           "operation": "extract_month"
         }
       ]
     }
   - Allowed operations: extract_month, extract_year, extract_day

5. "PIVOT"
   - Used to create a pivot table. Requires index, columns, and values.
   - Example Query: "pivot by Department as index, Location as columns, and average Salary as values"
   - JSON:
     {
       "operations": [
         {
           "type": "PIVOT",
           "index": "Department",
           "columns": "Location",
           "values": "Salary",
           "agg_func": "average"
         }
       ]
     }
6. "JOIN"
   - Used to combine data from two different sheets.
   - Example Query: "join 'Structured_Data' with 'Sales_Data' on 'EmployeeID'"
   - JSON:
     {
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
   - Allowed join_type: inner, left, right.

7. "UNSTRUCTURED_OP" (Optional)
   - Used to analyze text and create a new column.
   - Example Query: "analyze the sentiment of 'CustomerFeedback' and call it 'Sentiment'"
   - JSON:
     {
       "operations": [
         {
           "type": "UNSTRUCTURED_OP",
           "operation": "sentiment_analysis",
           "source_column": "CustomerFeedback",
           "new_column": "Sentiment"
         }
       ]
     }
   - Example Query: "summarize the 'ProductReview' column"
   - JSON:
     {
       "operations": [
         {
           "type": "UNSTRUCTURED_OP",
           "operation": "text_summary",
           "source_column": "ProductReview",
           "new_column": "Review_Summary"
         }
       ]
     }
   - Allowed operations: sentiment_analysis, text_summary.
"""

def build_analysis_prompt(schema: Dict[str, List[str]], user_query: str) -> str:
    """
    Builds the full prompt to send to the LLM.

    Args:
        schema: The schema dictionary from get_excel_schema
        user_query: The user's natural language Query
    
    Returns:
        The complete prompt string.
    """

    schema_string = ""
    for sheet_name, columns in schema.items():
        schema_string += f"Sheet: {sheet_name}\nColumns: {columns}\n\n"
    
    final_prompt = f"""

{OPERATION_PROMPT_GUIDELINES}

---
Here is the schema of the Excel File you must use:
{schema_string}
---
Here is the user's query:
"{user_query}"

Your JSON Plan:
"""
    return final_prompt


if __name__ == "__main__":
    test_schema = {
        'Structured_Data': [
            'EmployeeID', 'Name', 'Department', 'Age', 'Salary', 
            'JoiningDate', 'Performance_Score', 'Years_Experience', 
            'Location', 'Status'
        ],
        'Unstructured_Data': [
            'RecordID', 'CustomerFeedback', 'IssueDescription', 
            'ProductReview', 'AccountSummary'
        ]
    }

    test_query = "What is the average salary for the IT department?"

    prompt = build_analysis_prompt(test_schema, test_query)

    print(prompt)