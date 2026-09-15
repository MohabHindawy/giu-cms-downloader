@echo off
if not exist .venv (
    echo First-time setup: installing Python packages...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

python setup_wizard.py
pause