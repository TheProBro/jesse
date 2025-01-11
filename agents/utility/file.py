import os
from langchain_core.tools import StructuredTool

def create_file(file_path: str, content: str = "") -> str:
    """
    Creates a file at the specified path with the given content.
    
    Args:
        file_path (str): The path where the file should be created.
        content (str): The content to write into the file (default is an empty string).
            
    Returns:
        str: A message indicating whether the file was created successfully or not.
    """
    file_path = "/dump/" + file_path
    with open(file_path, "w") as file:
        file.write(content)
    return f"File created: {file_path}"

create_file_tool = StructuredTool.from_function(
    name="create_file",
    func=create_file,
    description=(
        "Creates a file at the specified path with the given content.\n\n"
        "Function: create_file\n"
        "Arguments: file_path (str), content (str)\n"
        "Return Type: str\n"
        "Returns a message indicating whether the file was created successfully."
    )
)

def read_file(file_path: str) -> str:
    """
    Reads and returns the content of a file at the specified path.
    
    Args:
        file_path (str): The path of the file to read.
            
    Returns:
        str: The content of the file, or an error message if the file does not exist.
    """
    file_path = "/dump/" + file_path
    if not os.path.exists(file_path):
        return f"Error: File does not exist: {file_path}"
    with open(file_path, "r") as file:
        return file.read()

read_file_tool = StructuredTool.from_function(
    name="read_file",
    func=read_file,
    description=(
        "Reads and returns the content of a file at the specified path.\n\n"
        "Function: read_file\n"
        "Arguments: file_path (str)\n"
        "Return Type: str\n"
        "Returns the content of the file or an error message if the file doesn't exist."
    )
)

def delete_file(file_path: str) -> str:
    """
    Deletes a file at the specified path.
    
    Args:
        file_path (str): The path of the file to delete.
            
    Returns:
        str: A message indicating whether the file was deleted successfully or not.
    """
    file_path = "/dump/" + file_path
    if not os.path.exists(file_path):
        return f"Error: File does not exist: {file_path}"
    os.remove(file_path)
    return f"File deleted: {file_path}"

delete_file_tool = StructuredTool.from_function(
    name="delete_file",
    func=delete_file,
    description=(
        "Deletes a file at the specified path.\n\n"
        "Function: delete_file\n"
        "Arguments: file_path (str)\n"
        "Return Type: str\n"
        "Returns a message indicating whether the file was deleted successfully."
    )
)
