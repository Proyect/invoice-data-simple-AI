@echo off
cd /d "%~dp0\.."
if not exist frontend\.env (
  if exist frontend\env.example (
    copy frontend\env.example frontend\.env
  )
)
cd frontend
npm run start
pause
