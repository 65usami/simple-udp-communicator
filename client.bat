@echo off

call venv_windows\Scripts\activate.bat
python client.py %1 %2
call venv_windows\Scripts\deactivate.bat
