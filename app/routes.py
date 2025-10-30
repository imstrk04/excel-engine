from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import os
import json

from excel_engine.schema_extractor import get_excel_schema
from excel_engine.prompt_builder import build_analysis_prompt
from excel_engine.llm_client import get_llm_json_response
from excel_engine.interpreter import PlanInterpreter

router = APIRouter(prefix="/api", tags=["Analysis"])

class AnalysisRequest(BaseModel):
    file_path: str
    query: str

@router.post("/analyse")
async def analyse_excel(request: AnalysisRequest = Body(...)):

    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    print(f"\n--- New Request Received ---")
    print(f"File: {request.file_path}")
    print(f"Query: {request.query}")

    try:
        print("Step 2: Getting schema...")
        schema = get_excel_schema(request.file_path)

        print("Step 3: Building prompt...")
        prompt = build_analysis_prompt(schema, request.query)
        
        print("Step 4: Getting JSON plan from LLM...")
        json_plan = get_llm_json_response(prompt)
        print(f"Plan received: {json.dumps(json_plan, indent=2)}")

        print("Step 5: Initializing interpreter...")
 
        interpreter = PlanInterpreter(file_path=request.file_path)
        
        print("Step 6: Executing plan...")
        result_data = interpreter.execute_plan(json_plan)
        print("Step 6: Execution complete.")

        return {
            "status": "success",
            "query": request.query,
            "result": result_data
        }


    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found during processing: {e}")
    
    except ValueError as e:
        print(f"VALIDATION ERROR: {e}")
        raise HTTPException(status_code=400, detail=f"Bad Request: {e}")
        
    except Exception as e:
        print(f"INTERNAL SERVER ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")