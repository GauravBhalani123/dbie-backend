@echo off
echo ==============================================
echo Deep Business Intelligence Engine - Auto Start
echo ==============================================

echo [1/3] Setting up Python Backend Server...
cd backend
python -m pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email] pydantic-settings
echo Starting Backend...
start "DBIE Backend" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [2/3] Setting up React Frontend...
cd ..\frontend
call npm install
echo Starting Frontend...
start "DBIE Frontend" cmd /k "npm run dev"

echo.
echo ==============================================
echo [3/3] ALL DONE!
echo The Backend API is running at: http://localhost:8000
echo The Frontend Dashboard is at: http://localhost:5173
echo ==============================================
pause
