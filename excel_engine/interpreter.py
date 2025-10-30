import pandas as pd
import json
from typing import Dict, List, Any

class PlanInterpreter:

    def __init__(self, file_path: str):
        print(f"Initialising Interpreter and loading data from {file_path}")
        try:

            self.dataframes = pd.read_excel(file_path, sheet_name=None)
            print(f"Data Loaded. Sheets found: {list(self.dataframes.keys())}")
        except FileNotFoundError:
            print(f"Error: File not found")
            raise
        except Exception as e:
            print("Error. Could not read Excel file")
            raise
    
    def execute_plan(self, plan: Dict[str, Any]) -> Any:
        """
        Executes the operations in the JSON plan sequentially.
        """
        
        target_sheet = plan.get('target_sheet')
        if not target_sheet or target_sheet not in self.dataframes:
            raise ValueError(f"Invalid or missing 'target_sheet' in plan. Found: {target_sheet}")

        current_df = self.dataframes[target_sheet].copy()
        final_result = None
        
        for op in plan['operations']:
            op_type = op.get('type')
            print(f"Executing operation: {op_type}")
            
            if op_type == 'FILTER':
                current_df = self._handle_filter(op, current_df)
            
            elif op_type == 'AGGREGATE':
                final_result = self._handle_aggregate(op, current_df)
                break
            
            elif op_type == 'MATH':
                current_df = self._handle_math(op, current_df)
            
            elif op_type == 'DATE_OP':
                current_df = self._handle_date_op(op, current_df)
            
            elif op_type == 'PIVOT':
                current_df = self._handle_pivot(op, current_df)
            
            elif op_type == 'JOIN':
                current_df = self._handle_join(op)
            
            else:
                print(f"WARNING: Unknown operation type '{op_type}'. Skipping.")
        
        if final_result is not None:
            print("Returning aggregated result.")
            return final_result
        else:
            print("Returning transformed DataFrame.")
            return json.loads(current_df.to_json(orient='records'))
        
    def _handle_filter(self, op, current_df):
        conditions = op.get('conditions', [])

        for cond in conditions:
            col = cond['column']
            op_str = cond['operator']
            val = cond['value']

            if col not in current_df.columns:
                raise ValueError(f"Filter error: Column '{col}' not Found")
            
            if op_str == "==":
                current_df = current_df[current_df[col] == val]
            elif op_str == '!=':
                current_df = current_df[current_df[col] != val]
            elif op_str == '>':
                current_df = current_df[current_df[col] > val]
            elif op_str == '<':
                current_df = current_df[current_df[col] < val]
            elif op_str == '>=':
                current_df = current_df[current_df[col] >= val]
            elif op_str == '<=':
                current_df = current_df[current_df[col] <= val]
                
        return current_df

    def _handle_aggregate(self, op, current_df):
        aggregations = op.get('aggregations', [])
        results = {}
        
        for agg in aggregations:
            col = agg['column']
            func = agg['function']
            
            if col not in current_df.columns:
                raise ValueError(f"Aggregate error: Column '{col}' not found.")
                
            result_key = f"{func}_of_{col}"
            
            if func == 'average':
                results[result_key] = float(current_df[col].mean())
            elif func == 'sum':
                results[result_key] = int(current_df[col].sum())
            elif func == 'min':
                results[result_key] = int(current_df[col].min())
            elif func == 'max':
                results[result_key] = int(current_df[col].max())
            elif func == 'count':
                results[result_key] = int(current_df[col].count())
                
        return results
    
    def _handle_math(self, op, current_df):
        new_col = op['new_column']
        expr = op['expression']
        
        col1 = expr['col1']
        op_str = expr['operator']
        val = expr['value'] 
        
    
        if isinstance(val, str) and val in current_df.columns:
            col2 = current_df[val]
        else:
            col2 = val
            
        if op_str == '+':
            current_df[new_col] = current_df[col1] + col2
        elif op_str == '-':
            current_df[new_col] = current_df[col1] - col2
        elif op_str == '*':
            current_df[new_col] = current_df[col1] * col2
        elif op_str == '/':
            current_df[new_col] = current_df[col1] / col2
            
        return current_df

    def _handle_date_op(self, op, current_df):
        new_col = op['new_column']
        source_col = op['source_column']
        date_op = op['operation']

        current_df[source_col] = pd.to_datetime(current_df[source_col])
        
        if date_op == 'extract_month':
            current_df[new_col] = current_df[source_col].dt.month
        elif date_op == 'extract_year':
            current_df[new_col] = current_df[source_col].dt.year
        elif date_op == 'extract_day':
            current_df[new_col] = current_df[source_col].dt.day
            
        return current_df

    def _handle_join(self, op):
        left_sheet = op['left_sheet']
        right_sheet = op['right_sheet']
        join_type = op['join_type']
        on_col = op['on_column']
        
        left_df = self.dataframes[left_sheet].copy()
        right_df = self.dataframes[right_sheet].copy()
        
        joined_df = pd.merge(left_df, right_df, on=on_col, how=join_type)
        
        return joined_df

    def _handle_pivot(self, op, current_df):
        index = op['index']
        columns = op['columns']
        values = op['values']
        agg_func = op['agg_func'] 
        
    
        if agg_func == 'average':
            agg_func_pandas = 'mean'
        else:
            agg_func_pandas = agg_func 
        
        pivot_df = pd.pivot_table(
            current_df, 
            values=values, 
            index=index, 
            columns=columns, 
            aggfunc=agg_func_pandas
        )
        
        return pivot_df.reset_index()
    

if __name__ == "__main__":
    
    try:
        interpreter = PlanInterpreter(file_path='data/synthetic_data.xlsx')

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
                        { "column": "Salary", "function": "average" },
                        { "column": "Age", "function": "max" }
                    ]
                }
            ]
        }
        
        print(f"\n---Executing Test Plan---")
        print(f"Plan: {json.dumps(test_plan, indent=2)}")
        
        result = interpreter.execute_plan(test_plan)
        
        print("\n---Final Result---")
        print(json.dumps(result, indent=2))
        
        test_plan_2 = {
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
        
        print("\n---Executing Test Plan 2 (Math)---")
        result_2 = interpreter.execute_plan(test_plan_2)
        print("\n---Final Result (First 5 Rows)---")
        print(json.dumps(result_2[:5], indent=2)) 
        
        # --- Test 3: Date Operation ---
        test_plan_3 = {
            "target_sheet": "Structured_Data",
            "operations": [
                {
                    "type": "DATE_OP",
                    "new_column": "Joining_Year",
                    "source_column": "JoiningDate",
                    "operation": "extract_year"
                }
            ]
        }
        
        print("\n--- Executing Test Plan 3 (Date) ---")
        result_3 = interpreter.execute_plan(test_plan_3)
        print("\n--- Final Result (First 5 Rows) ---")
        print(json.dumps(result_3[:5], indent=2))

        # --- Test 4: Pivot Operation ---
        test_plan_4 = {
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
        
        print("\n--- Executing Test Plan 4 (Pivot) ---")
        result_4 = interpreter.execute_plan(test_plan_4)
        print("\n--- Final Result (First 5 Rows) ---")
        print(json.dumps(result_4[:5], indent=2))
        
        test_plan_5 = {
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
        
        print("\n--- Executing Test Plan 5 (Join) ---")
        interpreter_with_join = PlanInterpreter(file_path='data/synthetic_data.xlsx')
        result_5 = interpreter_with_join.execute_plan(test_plan_5)
        print("\n--- Final Result (First 5 Rows) ---")
        print(json.dumps(result_5[:5], indent=2))

    except Exception as e:
        print(f"\n---TEST FAILED---")
        print(e)