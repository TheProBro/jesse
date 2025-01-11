import subprocess
import os
from langchain_core.tools import StructuredTool

# Function to find AUMID by app name
def find_aumid(app_name):
    """
    Finds the AUMID (App User Model ID) for a given application name using PowerShell.

    Args:
        app_name (str): The name of the application to search for.

    Returns:
        str: The AUMID of the application if found, or None otherwise.
    """
    result = subprocess.run(["powershell", "get-StartApps"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if app_name.lower() in line.lower():
            parts = line.split()
            if len(parts) > 1:
                return parts[1]
    return None

# Function to launch the app by its AUMID
def launch_application(app_name: str) -> str:
    """
    Launches an application by finding its AUMID and running it.

    Args:
        app_name (str): The name of the application to launch.

    Returns:
        str: A message indicating whether the app was launched successfully or not.
    """
    aumid = find_aumid(app_name)
    if aumid:
        os.system(f'start explorer shell:appsfolder\\{aumid}')
        return f"Application launched: {app_name} (AUMID: {aumid})"
    else:
        return f"Error: Application '{app_name}' not found!"

# Function to close the app by its executable name
def close_application(app_name: str) -> str:
    """
    Closes an application by its executable name using taskkill.

    Args:
        app_name (str): The name of the application executable to close.

    Returns:
        str: A message indicating whether the app was closed successfully or not.
    """
    try:
        subprocess.run(["taskkill", "/IM", f"{app_name}.exe", "/F"], check=True)
        return f"Application '{app_name}' closed successfully."
    except subprocess.CalledProcessError:
        return f"Error: Failed to close application '{app_name}'. It may not be running."

# Wrap the launch_application function in a StructuredTool
launch_application_tool = StructuredTool.from_function(
    name="launch_application",
    func=launch_application,
    description=(
        "Launches an application by finding its AUMID and running it.\n\n"
        "Function: launch_application\n"
        "Arguments: app_name (str)\n"
        "Return Type: str\n"
        "Returns a message indicating whether the application was launched successfully or not."
    ),
)

# Wrap the close_application function in a StructuredTool
close_application_tool = StructuredTool.from_function(
    name="close_application",
    func=close_application,
    description=(
        "Closes an application by its executable name using taskkill.\n\n"
        "Function: close_application\n"
        "Arguments: app_name (str)\n"
        "Return Type: str\n"
        "Returns a message indicating whether the application was closed successfully or not."
    ),
)
