@echo off
cd /d "%~dp0backend"
echo Installing requirements (first time only)...
python -m pip install -r requirements.txt
echo Starting MediGen AI - browser will open automatically...
python main.py
pause
