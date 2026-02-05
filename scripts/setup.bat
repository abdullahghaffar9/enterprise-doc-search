@echo off
REM Quick Setup & Test Script for AI Document Q&A System (Windows)

setlocal enabledelayedexpansion
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

echo ==========================================
echo AI Document Q&A System - Setup ^& Test
echo ==========================================
echo.

REM 1. Check Python
echo %YELLOW%[1/5] Checking Python...%NC%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python not found%NC%
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%✅ Python !PYTHON_VERSION!%NC%
echo.

REM 2. Check Node.js
echo %YELLOW%[2/5] Checking Node.js...%NC%
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Node.js not found%NC%
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo %GREEN%✅ Node.js !NODE_VERSION!%NC%
echo.

REM 3. Check .env file
echo %YELLOW%[3/5] Checking .env configuration...%NC%
if not exist ".env" (
    echo %RED%❌ .env file not found%NC%
    echo Creating .env from template...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    ) else (
        echo Please create .env file manually
    )
    echo %YELLOW%⚠️  Update .env with your API keys:%NC%
    echo - PINECONE_API_KEY
    echo - GROQ_API_KEY
    exit /b 1
)
echo %GREEN%✅ .env exists (verify API keys are populated)%NC%
echo.

REM 4. Check dependencies
echo %YELLOW%[4/5] Checking dependencies...%NC%
echo Backend requirements...
if exist "backend\requirements.txt" (
    if not exist ".venv" (
        echo Creating virtual environment...
        python -m venv .venv
    )
    call .venv\Scripts\activate.bat
    echo Installing packages (this may take a minute)...
    pip install -q -r backend\requirements.txt
    echo %GREEN%   ✅ Backend dependencies ready%NC%
)

echo Frontend dependencies...
if exist "frontend\package.json" (
    cd frontend
    if not exist "node_modules" (
        echo Installing packages (this may take a minute)...
        call npm install -q
    )
    echo %GREEN%   ✅ Frontend dependencies ready%NC%
    cd ..
)
echo.

REM 5. Show next steps
echo %YELLOW%[5/5] Setup Complete!%NC%
echo.
echo %GREEN%Next steps:%NC%
echo 1. Update .env with your API keys:
echo    - PINECONE_API_KEY: Get from https://pinecone.io/console
echo    - GROQ_API_KEY: Get from https://console.groq.com
echo    - PINECONE_INDEX_NAME: Your index from Pinecone
echo.
echo 2. Start the application:
echo    Option A (Combined): python start_app.py
echo    Option B (Separate terminals):
echo       Backend:  cd backend ^&^& python -m uvicorn app.main:app --reload --port 8000
echo       Frontend: cd frontend ^&^& npm run dev
echo.
echo 3. Open http://localhost:5173 in your browser
echo.
echo %GREEN%Happy coding!%NC%

endlocal
