@echo off

call venvs\venv_windows\Scripts\activate.bat
python server.py %1
call venvs\venv_windows\Scripts\deactivate.bat
