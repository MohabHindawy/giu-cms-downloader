import os
from pathlib import Path
from dotenv import load_dotenv
from paths import get_app_dir

load_dotenv(get_app_dir() / ".env")

GIU_USERNAME = os.environ["GIU_USERNAME"]
GIU_PASSWORD = os.environ["GIU_PASSWORD"]
BASE_URL = "https://cms.giu-uni.de"
REQUEST_TIMEOUT = 60

_download_root_env = os.environ.get("DOWNLOAD_ROOT", "").strip()
if _download_root_env:
    DOWNLOAD_ROOT = Path(_download_root_env)
else:
    DOWNLOAD_ROOT = Path.home() / "Downloads" / "GIU"

DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)