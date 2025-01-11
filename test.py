import subprocess
import os

# Function to find AUMID by app name
def find_aumid(app_name):
    # Run PowerShell command to get all installed apps
    result = subprocess.run(["powershell", "get-StartApps"], capture_output=True, text=True)
    
    # Split the output into lines and search for the app
    for line in result.stdout.splitlines():
        if app_name.lower() in line.lower():
            # Extract and return the AUMID (AppID) from the line
            parts = line.split()
            if len(parts) > 1:
                return parts[1]
    return None

# Function to launch the app by its AUMID
def launch_app(aumid):
    if aumid:
        os.system(f'start explorer shell:appsfolder\\{aumid}')
        print(f"Launching {aumid}...")
    else:
        print("App not found!")

# Example: Search for and launch "Weather" app
app_name = "Notepad"
aumid = find_aumid(app_name)

# Launch if found
launch_app(aumid)
