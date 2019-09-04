@echo off

call venv_windows\Scripts\activate.bat
python server.py %1
call venv_windows\Scripts\deactivate.bat
