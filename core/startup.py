import os
import sys
from pathlib import Path

from paths import get_app_dir


def get_launch_command() -> str:
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable)
        return f'"{exe}" --tray'
    else:
        py = Path(sys.executable)
        app_py = get_app_dir() / "app.py"
        return f'"{py}" "{app_py}" --tray'


def is_in_startup() -> bool:
    if sys.platform != "win32":
        return False

    startup_dir = Path(
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    )
    link_path = startup_dir / "GIU_CMS_Downloader.bat"
    return link_path.exists()


def add_to_startup() -> str | None:
    if sys.platform != "win32":
        return "Automatic startup is only supported on Windows."

    cmd = get_launch_command()
    try:
        startup_dir = Path(
            os.path.expandvars(
                r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
            )
        )
        startup_dir.mkdir(parents=True, exist_ok=True)
        link_path = startup_dir / "GIU_CMS_Downloader.bat"

        bat_content = f'@echo off\nstart "" {cmd}\n'
        link_path.write_text(bat_content)
        return None
    except Exception as e:
        return str(e)


def remove_from_startup() -> str | None:
    if sys.platform != "win32":
        return "Automatic startup is only supported on Windows."

    try:
        startup_dir = Path(
            os.path.expandvars(
                r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
            )
        )
        link_path = startup_dir / "GIU_CMS_Downloader.bat"
        if link_path.exists():
            link_path.unlink()
        return None
    except Exception as e:
        return str(e)
