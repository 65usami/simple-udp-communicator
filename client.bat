@echo off

call venvs\venv_windows\Scripts\activate.bat
python client.py %1 %2
call venvs\venv_windows\Scripts\deactivate.bat
