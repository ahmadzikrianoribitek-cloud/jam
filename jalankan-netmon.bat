@echo off
pip install psutil -q
start "" pythonw "%~dp0netmon.py"
