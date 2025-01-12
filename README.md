# AI Assistant with Face Recognition and Speech-to-Text Integration

This project is an AI assistant system that combines face recognition for user authentication and a speech-to-text interface to interact with users. The assistant is powered by **Langchain** and **LangGraph** frameworks for natural language understanding and task execution.

## Features

- **Face Recognition**: Registers and authenticates users through face encoding.
- **Speech-to-Text Interaction**: Processes user input via speech and converts it into text for further processing.
- **Task Execution**: Handles user requests by leveraging Langchain tools and LangGraph for planning and execution.
- **Context-Aware Responses**: Delivers responses based on both historical interactions and the current user input.

---

## Installation

### Prerequisites

- Python 3.8 or above
- Required libraries (install using `pip`):
  - `langchain`
  - `langgraph`
  - `pydantic`
  - `speechrecognition`
  - `opencv-python`
  - `dlib`

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-url.git
   cd your-repo-folder

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt


3. Set up environment variables:
    ```bash
    GROQ_API_KEY
    TAVILY_API_KEY 
    
These keys are required for API access and will be prompted during runtime.

4. Go to agents/ folder and then run the below command

    ```bash
    python test4.py



### Contributors

```
Team Adieu