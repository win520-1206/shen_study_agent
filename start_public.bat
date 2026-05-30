@echo off
echo Starting LearnMate-AI (Public Mode)...
echo.
start "Server" /D "C:\shen_study_agent" "C:\Users\23120\anaconda3\python.exe" -m uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000
timeout /t 4 /nobreak >nul
echo Local server started: http://localhost:8000
echo.
echo Starting public tunnel...
echo Wait for a URL like https://xxx.trycloudflare.com
echo Share that URL with anyone!
echo.
cloudflared.exe tunnel --url http://localhost:8000
pause
