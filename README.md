# Petavue Excel AI Engine

This is an AI-powered REST API designed to analyze and manipulate Excel files using natural language queries. This engine leverages a Large Language Model (LLM) to parse user intent, which is then executed by a secure, custom-built interpreter written in Python.

This project was developed as a technical assignment for Petavue.

## Problem Statement

The objective is to develop an AI engine capable of reading and analyzing data in Excel sheets. The engine must support natural language queries for complex data operations, including aggregations, mathematical operations, joins, pivots, and date-time manipulation.

A critical constraint of the project is that **"the core algorithm or approach... must be original and developed independently"**. The use of pre-existing libraries that translate natural language to code (such as `pandas-ai`) is strictly prohibited.

-----

## Core Algorithm: Design and Rationale

The central challenge is to translate an unstructured natural language query into a structured data operation without using pre-built libraries for this specific task. Several approaches were considered.

### Rejected Approach 1: Direct Code Generation (eval())

  * **How it Works:** The system would feed the user's query and the Excel schema to an LLM, prompting it to return executable Python (pandas) code as a string. The server would then execute this code using `eval()` or `exec()`.
  * **Why it was Rejected:**
      * **Security:** This approach presents a catastrophic security risk. It makes the server highly vulnerable to prompt injection attacks, where a malicious query could trick the LLM into generating code that accesses the filesystem (`os.system('rm -rf /')`), exfiltrates data, or performs other arbitrary code execution.
      * **Originality:** This directly violates the project's core originality constraint. The LLM, not the developer, is writing the "core algorithm".
      * **Reliability:** LLM-generated code can be buggy, inefficient, or syntactically incorrect, leading to unpredictable runtime errors.

### Rejected Approach 2: LLM Tool/Function Calling

  * **How it Works:** This involves defining Python functions for each operation (e.g., `def filter_data(...)`). An advanced LLM (like OpenAI's GPT or Google's Gemini) is then used in "function calling" mode to parse the query and decide which function to call with which arguments.
  * **Why it was Rejected:**
      * **Originality (Gray Area):** This is a "gray area". The "core algorithm" effectively becomes the LLM's proprietary, black-box reasoning model that decides which tool to use. This still relies on a pre-built, non-original decision engine, which may not satisfy the originality requirement.
      * **Dependency:** This approach tightly couples the project to a specific, advanced LLM API, reducing portability.

### Final Algorithm: The Intent-Based Operation Engine

This project implements a secure, hybrid approach that decouples parsing from execution. This ensures the originality requirement is met in full. The system is split into two parts:

1.  **The Parser (The LLM):** The LLM's **only** job is to act as a parser. It translates the user's unstructured query into a simple, predictable JSON "plan" that represents the user's *intent*. It does not write any code.

2.  **The Interpreter (The "Original Algorithm"):** This is the core, original component of the project. It is a custom-built Python class (`PlanInterpreter`) that receives the JSON plan. It validates this plan and then executes the required operations in sequence using standard, safe pandas functions.

#### Example Flow:

1.  **User Query:** "What is the average salary for the IT department?"

2.  **LLM JSON Plan:** The LLM parses this query (using instructions from `prompt_builder.py`) and returns a simple JSON object:

    ```json
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
    ```

3.  **Interpreter Execution:** The `PlanInterpreter` receives this JSON.

      * It loops through the `operations` array.
      * For the first operation, it sees `"type": "FILTER"` and calls its internal `_handle_filter` method, which safely builds a pandas filter.
      * For the second operation, it sees `"type": "AGGREGATE"` and calls its internal `_handle_aggregate` method, which safely performs a pandas `.mean()` on the filtered data.
      * The final result (the average salary) is returned.

#### Why this Approach is Superior:

  * **Originality:** The `PlanInterpreter` class is 100% original code. It is the "core algorithm" that intelligently maps a structured plan to a series of data operations. This fulfills the originality requirement.
  * **Security:** No `eval()` is used. The attack surface is limited to parsing a known JSON schema. Malicious prompts will only result in invalid JSON or a valid plan that fails safely (e.g., "filter on a column that does not exist").
  * **Testability:** The interpreter can be (and is) fully unit-tested in isolation from the LLM, proving its logical correctness.
  * **Reliability:** It is far more reliable to prompt an LLM for simple, structured JSON than it is for syntactically perfect Python code.

-----

## Tech Stack

  * **Backend:** FastAPI, Uvicorn
  * **Data Handling:** Pandas
  * **LLM:** Ollama (with Llama 3.1)
  * **Testing:** Pytest, HTTPX (for `TestClient`)
  * **Containerization:** Docker

-----

## Project Structure

```
petavue-excel-engine/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app initialization
│   ├── routes.py              # API endpoint logic
├── examples/
│   ├── examples.txt          # Example input of each operations
├── excel_engine/
│   ├── __init__.py
│   ├── interpreter.py         # The "core original algorithm"
│   ├── llm_client.py          # Client to connect to Ollama
│   ├── prompt_builder.py      # Creates the prompt for the LLM
│   └── schema_extractor.py    # Reads sheet/column names from Excel
├── scripts/
│   └── generate_data.py       # Generates synthetic .xlsx data
├── tests/
│   ├── __init__.py
│   ├── test_api.py            # Integration tests for the API
│   └── test_interpreter.py    # Unit tests for the interpreter
├── data/
│   └── synthetic_data.xlsx    # (Ignored by git)
├── .dockerignore
├── .gitignore
├── Dockerfile                 # Docker build instructions
└── requirements.txt
```

-----

## Setup and Installation

### 1\. Prerequisites

  * Python 3.10+
  * [Ollama](https://ollama.com/) (or another LLM service)
  * [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for containerization)

### 2\. Local Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/petavue-excel-engine.git
    cd petavue-excel-engine
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Generate test data:**

    ```bash
    python scripts/generate_data.py
    ```

5.  **Run the Ollama LLM Server:**
    Ensure the Ollama server is running in a separate terminal and has the required model.

    ```bash
    ollama serve
    ollama pull llama3.1
    ```

-----

## Usage

### Running the API Server

1.  **Start the Uvicorn server:**
    ```bash
    uvicorn app.main:app --reload
    ```
2.  **Access the API Documentation:**
    The API provides interactive documentation (via Swagger UI) which satisfies the project's documentation requirement.
    Navigate to: **`http://127.0.0.1:8000/docs`**

### API Endpoint

#### `POST /api/analyse`

Analyzes an Excel file based on a natural language query.

**Request Body:**

```json
{
  "file_path": "data/synthetic_data.xlsx",
  "query": "What is the average salary for the IT department?"
}
```

**Success Response:**

```json
{
  "status": "success",
  "query": "What is the average salary for the IT department?",
  "result": {
    "average_of_Salary": 93569.43
  }
}
```

-----

## Testing

The project uses `pytest` for comprehensive unit and integration testing. Tests are located in the `tests/` directory.

  * `test_interpreter.py`: Contains unit tests that verify the logic of the `PlanInterpreter` in isolation, using mocked data and without making any LLM calls.
  * `test_api.py`: Contains integration tests that verify the API endpoints, error handling, and the connection of all modules.

**To run all tests:**

```bash
pytest
```

Expected output: `10 passed`

-----

## Docker Deployment

The project is fully containerized, satisfying the Docker integration requirement.

### Build the Image

From the project root, run:

```bash
docker build -t petavue-engine .
```

### Run the Container

This command runs the container and maps your local port 8000 to the container's port 8000. It also passes the `OLLAMA_HOST` environment variable, which is necessary for the container to find the Ollama server running on your host machine.

```bash
docker run -p 8000:8000 -e OLLAMA_HOST="http://host.docker.internal:11434" petavue-engine
```

The API will then be available at `http://localhost:8000/docs`.