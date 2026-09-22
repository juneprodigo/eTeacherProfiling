@echo off
echo Starting Teacher eProfile System...
echo ===================================

echo [1/2] Launching Django REST Backend on http://127.0.0.1:8000 ...
start "Teacher eProfile - Backend" cmd /k "cd backend && python manage.py runserver 127.0.0.1:8000"

timeout /t 2 >nul

echo [2/2] Launching Vue 3 Frontend on http://localhost:5173 ...
start "Teacher eProfile - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Application running!
echo Access the portal at: http://localhost:5173
echo Admin User:     admin / Admin@123456
echo HR Officer:     hr_officer / Hr@123456
echo Sample Teacher: teacher1 / Teacher@123456
pause
