@echo off
REM ============================================
REM AI-Powered Document Knowledge Base - Quick Start
REM ============================================

echo.
echo  ========================================
echo  AI Document Knowledge Base - Setup
echo  ========================================
echo.

REM Color codes
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"

echo %BLUE%[1/5] Checking Python installation...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Python not found. Please install Python 3.11+%RESET%
    exit /b 1
)
echo %GREEN%✓ Python installed%RESET%

echo.
echo %BLUE%[2/5] Setting up backend virtual environment...%RESET%
cd backend
if not exist ".venv" (
    python -m venv .venv
    echo %GREEN%✓ Virtual environment created%RESET%
) else (
    echo %GREEN%✓ Virtual environment already exists%RESET%
)

call .venv\Scripts\activate.bat
echo %GREEN%✓ Virtual environment activated%RESET%

echo.
echo %BLUE%[3/5] Installing backend dependencies...%RESET%
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo %GREEN%✓ Backend dependencies installed%RESET%

cd ..
echo.
echo %BLUE%[4/5] Checking Node.js installation...%RESET%
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%WARNING: Node.js not found. Frontend setup skipped.%RESET%
    echo %YELLOW%Install Node.js from https://nodejs.org%RESET%
) else (
    echo %GREEN%✓ Node.js installed%RESET%
    
    echo.
    echo %BLUE%[5/5] Installing frontend dependencies...%RESET%
    cd frontend
    call npm install --quiet
    echo %GREEN%✓ Frontend dependencies installed%RESET%
    cd ..
)

echo.
echo %GREEN%========================================%RESET%
echo %GREEN%✓ Setup complete!%RESET%
echo %GREEN%========================================%RESET%
echo.
echo %YELLOW%Next steps:%RESET%
echo.
echo  1. Backend (Terminal 1):
echo     cd backend
echo     .\.venv\Scripts\activate.ps1
echo     uvicorn app.main:app --reload
echo.
echo  2. Frontend (Terminal 2):
echo     cd frontend
echo     npm run dev
echo.
echo  3. Open browser and visit: http://localhost:5173
echo.
echo  4. Login with:
echo     Email: admin@company.com
echo     Password: admin123
echo.
echo %BLUE%Documentation: See SETUP_GUIDE.md for detailed instructions%RESET%
echo.
