import subprocess
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
import getpass
import os
from langchain_core.prompts import ChatPromptTemplate


def _get_pass(var: str):
    if var not in os.environ:
        os.environ[var] = getpass.getpass(f"{var}: ")


_get_pass("GROQ_API_KEY")

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

def set_volume(volume_level: int) -> str:
    """
    Sets the system volume to the specified level.
    
    Args:
        - volume_level (int): The target volume level as a percentage (0 to 100).
            
    Returns:
        str: A message indicating whether the volume was set successfully or if there was an error.
    """
    try:
        # Windows-specific volume control using `nircmd`
        subprocess.run(
            ["nircmd.exe", "setsysvolume", str(int(volume_level * 655.35))],
            check=True,
        )
        return f"Volume set to {volume_level}%."
    except FileNotFoundError:
        return (
            "Error: `nircmd` not found. Please ensure it's installed and added to PATH."
        )
    except Exception as e:
        return f"Error: Failed to set volume. Details: {str(e)}"

set_volume_tool = StructuredTool.from_function(
    name="set_volume",
    func=set_volume,
    description=(
        "Sets the system volume to the specified percentage. "
        "Volume level must be between 0 and 100.\n\n"
        "Function: set_volume\n"
        "Arguments: volume_level: int\n"
        "Return Type: str\n"
        "Returns a message indicating whether the volume was set successfully or if an error occurred."
    ),
)

def run_python_code(code_content: str) -> str:
    """
    Executes Python code provided as a string.

    Args:
        - code_content (str): The Python code to execute.

    Returns:
        str: The output of the executed code or an error message if execution fails.
    """
    try:
        print(code_content)  # Printing the original code content
        code_content = code_content.replace("{", "{{").replace("}", "}}")
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant that corrects the python syntax of the code. return only the corrected python code."),
                ("human", code_content),  # Directly inserting the code content
            ]
        )

        # Create the chain with the model
        chain = prompt | llm

        # Get the corrected code
        corrected_code = chain.invoke({"code_content": code_content}).content

        # Optionally, print the corrected code
        print("Corrected Code:")
        print(corrected_code)

        
        # Write the corrected code to a temporary Python file
        temp_file_path = "temp_script.py"
        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(corrected_code)

        # Execute the temporary Python script
        result = subprocess.run(
            ["C:/Users/Alank/Desktop/jesse/jesse_env/Scripts/python.exe", temp_file_path], check=True, text=True, capture_output=True, cwd=os.getcwd()
        )

        # Remove the temporary file after execution
        os.remove(temp_file_path)

        return f"Code executed successfully. Output:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error: Code execution failed. Details:\n{e.stderr}"
    except Exception as e:
        return f"Error: An unexpected error occurred. Details: {str(e)}"

# Define the tool
run_python_code_tool = StructuredTool.from_function(
    name="run_python_code",
    func=run_python_code,
    description=(
        "Executes Python code provided as a string. The tool will save the code to a temporary file, "
        "execute it, and return the output or an error message if execution fails.\n\n"
        "Function: run_python_code\n"
        "Arguments: code_content: str\n"
        "Return Type: str\n"
        "Returns a message indicating the result of the code execution."
    ),
)

