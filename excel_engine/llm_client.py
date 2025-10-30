import ollama
import json
from typing import Dict, Any

def get_llm_json_response(prompt, model= "llama3.1"):

    try:
        response = ollama.chat(
            model=model, 
            format='json',
            messages=[{'role': 'user', 'content': prompt}]
        )
        response_content = response['message']['content']

        json_plan = json.loads(response_content)

        return json_plan
    
    except ollama.ResponseError as e:
        print(f"OLLAMA ERROR: {e.error}")
        raise Exception(f"Ollama response error: {e.error}")
    except json.JSONDecodeError as e:
        print(f"JSON DECODE ERROR: The LLM did not return valid JSON.")
        print(f"Received: {response_content}")
        raise Exception("LLM failed to return valid JSON.")

def get_llm_text_response(prompt, model="llama3.1"):
    try:
        response = ollama.chat(
            model = model,
            format=None,
            messages= [
                {'role': 'user', 'content': prompt}
            ]
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"OLLAMA TEXT ERROR: {e}")
        return "ERROR"

if __name__ == "__main__":
    from prompt_builder import build_analysis_prompt

    test_schema = {
        'Structured_Data': ['EmployeeID', 'Name', 'Department', 'Age', 'Salary', 'JoiningDate', 'Location'],
    }

    test_query = "What is the average salary for the IT department?"

    prompt_to_send = build_analysis_prompt(test_schema, test_query)

    try:
        plan = get_llm_json_response(prompt_to_send)
        print("LLM Output:")
        print(json.dumps(plan, indent=2))
    except Exception as e:
        print(f"TEST FAILED because of {e}")
        