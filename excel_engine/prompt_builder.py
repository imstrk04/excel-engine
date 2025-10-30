# In: excel_engine/prompt_builder.py

# (This is the new, more robust set of rules)
OPERATION_PROMPT_GUIDELINES = """
You are a data analysis assistant. Your ONLY job is to convert a user's query into a structured JSON operation plan.
You MUST follow these rules:
- Only output the JSON plan. Do not add explanations or introductions.
- The root JSON object MUST have a "target_sheet" key.
- The plan is an array of operations. Operations are executed in order.
- Always use the exact column names provided in the schema.
- **CRITICAL RULE**: If a query involves both filtering and aggregation (e.g., 'average salary for IT'), your plan MUST include a `FILTER` operation first, followed by an `AGGREGATE` operation.

Here are the allowed operations:

1. "COMBINED (Filter + Aggregate)"
   - This is the most common pattern. Use this when the query asks for a calculation on a *subset* of data.
   - Example Query: "What is the average salary for the IT department?"
   - JSON:
     {
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

2. "FILTER" (Standalone)
   - Used *only* when the user asks for a raw list of data.
   - Example Query: "show me all employees in IT"
   - JSON:
     {
       "target_sheet": "Structured_Data",
       "operations": [
         {
           "type": "FILTER",
           "conditions": [
             { "column": "Department", "operator": "==", "value": "IT" }
           ]
         }
       ]
     }
   - Allowed operators: ==, !=, >, <, >=, <=

3. "AGGREGATE" (Standalone)
   - Used when the user asks for a calculation on the *entire* sheet.
   - Example Query: "what is the average salary and max age for everyone?"
   - JSON:
     {
       "target_sheet": "Structured_Data",
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

4. "MATH"
   - Used to create a new column by performing math on an existing one.
   - Example Query: "create a new column 'Bonus' that is Salary * 0.1"
   - JSON:
     {
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
   - Allowed operators: +, -, *, /

5. "DATE_OP"
   - Used to extract parts of a date.
   - Example Query: "extract the month from 'JoiningDate'"
   - JSON:
     {
       "target_sheet": "Structured_Data",
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

6. "PIVOT"
   - Used to create a pivot table. Requires index, columns, and values.
   - Example Query: "pivot by Department as index, Location as columns, and average Salary as values"
   - JSON:
     {
       "target_sheet": "Structured_Data",
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

7. "JOIN"
   - Used to combine data from two different sheets.
   - Example Query: "join 'Structured_Data' with 'Sales_Data' on 'EmployeeID'"
   - JSON:
     {
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
   - Allowed join_type: inner, left, right.

8. "UNSTRUCTURED_OP" (Optional)
   - Used to analyze text and create a new column.
   - Example Query: "analyze the sentiment of 'CustomerFeedback' and call it 'Sentiment'"
   - JSON:
     {
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
   - Allowed operations: sentiment_analysis, text_summary.
"""
def build_analysis_prompt(schema, user_query):
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