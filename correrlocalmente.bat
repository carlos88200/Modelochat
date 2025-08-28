@echo off

cd /d "%~dp0"

call .venv\Scripts\activate

fastapi run main.py


pause