import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GIU_USERNAME = os.environ["USERNAME"]
GIU_PASSWORD = os.environ["PASSWORD"]
BASE_URL = "https://cms.giu-uni.de"

_download_root_env = os.environ.get("DOWNLOAD_ROOT", "").strip()
if _download_root_env:
    DOWNLOAD_ROOT = Path(_download_root_env)
else:
    DOWNLOAD_ROOT = Path.home() / "Downloads" / "GIU"

DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)