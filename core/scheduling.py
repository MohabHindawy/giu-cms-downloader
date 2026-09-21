import subprocess
import sys
from pathlib import Path
from paths import get_app_dir

TASK_NAME = "GIU CMS Downloader"

def get_command() -> str:
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable)
        return f'"{exe}" --headless'
    else:
        # Running as python script
        py = Path(sys.executable)
        app_py = get_app_dir() / "app.py"
        return f'"{py}" "{app_py}" --headless'

def is_task_installed() -> bool:
    if sys.platform != "win32":
        return False
        
    try:
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", TASK_NAME],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        )
        return result.returncode == 0
    except Exception:
        return False

def install_task(interval: str = "1 Hour") -> str | None:
    if sys.platform != "win32":
        return "Scheduling is only supported on Windows."
        
    cmd = get_command()
    
    # Translate UI string to schtasks arguments
    if interval == "30 Minutes":
        sc, mo = "MINUTE", "30"
    elif interval == "1 Hour":
        sc, mo = "HOURLY", "1"
    elif interval == "2 Hours":
        sc, mo = "HOURLY", "2"
    elif interval == "4 Hours":
        sc, mo = "HOURLY", "4"
    elif interval == "12 Hours":
        sc, mo = "HOURLY", "12"
    elif interval == "Daily":
        sc, mo = "DAILY", "1"
    else:
        sc, mo = "HOURLY", "1"

    try:
        result = subprocess.run(
            [
                "schtasks",
                "/Create",
                "/TN",
                TASK_NAME,
                "/TR",
                cmd,
                "/SC",
                sc,
                "/MO",
                mo,
                "/RL",
                "LIMITED",
                "/F",
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        )
        if result.returncode == 0:
            return None
        return f"Failed to create task:\n{result.stderr}"
    except Exception as e:
        return str(e)

def remove_task() -> str | None:
    if sys.platform != "win32":
        return "Scheduling is only supported on Windows."
        
    try:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        )
        if result.returncode == 0:
            return None
        return f"Failed to delete task:\n{result.stderr}"
    except Exception as e:
        return str(e)
