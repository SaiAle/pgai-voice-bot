@echo off
cd /d "%~dp0"
echo Starting LiveKit voice bot...
".venv-livekit\Scripts\python.exe" agent.py dev
pause
