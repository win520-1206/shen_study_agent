@echo off
echo Starting LearnMate-AI...
start "Server" /D "C:\shen_study_agent" "C:\Users\23120\anaconda3\python.exe" -m uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000
timeout /t 4 /nobreak >nul
start http://localhost:8000
echo Done! Browser opened.
pause
