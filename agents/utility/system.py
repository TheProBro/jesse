import subprocess
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

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
