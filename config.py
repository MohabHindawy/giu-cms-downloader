import os
from dotenv import load_dotenv

load_dotenv()

GIU_USERNAME = os.environ["USERNAME"]
GIU_PASSWORD = os.environ["PASSWORD"]
BASE_URL = "https://cms.giu-uni.de"

DOWNLOAD_ROOT = "./Downloads"
FOLDER_TEMPLATE = "{course_code} - {course_name}/{week_label}"
FILE_TEMPLATE = "{number} - {title} ({item_type}){ext}"