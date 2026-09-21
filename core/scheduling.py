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

def install_task() -> str | None:
    if sys.platform != "win32":
        return "Scheduling is only supported on Windows."
        
    cmd = get_command()
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
                "HOURLY",
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
