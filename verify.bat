@echo off
REM ============================================
REM AI Document Knowledge Base - Verification
REM ============================================

setlocal enabledelayedexpansion
set TESTS_PASSED=0
set TESTS_FAILED=0

echo.
echo ========================================
echo Verification Script
echo ========================================
echo.

REM Test 1: Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    ❌ FAILED: Python not found
    set /a TESTS_FAILED+=1
) else (
    python --version
    echo    ✓ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 2: Virtual Environment
echo.
echo [2/8] Checking Python virtual environment...
if exist "backend\.venv" (
    echo    ✓ PASSED: Virtual environment exists
    set /a TESTS_PASSED+=1
) else (
    echo    ❌ FAILED: Virtual environment not found
    echo    Run: python -m venv backend\.venv
    set /a TESTS_FAILED+=1
)

REM Test 3: Backend Dependencies
echo.
echo [3/8] Checking backend dependencies...
cd backend >nul 2>&1
call .venv\Scripts\activate.bat >nul 2>&1
pip list | findstr /i "fastapi uvicorn sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo    ❌ FAILED: Dependencies not installed
    echo    Run: pip install -r requirements.txt
    set /a TESTS_FAILED+=1
) else (
    echo    ✓ PASSED: Core dependencies installed
    set /a TESTS_PASSED+=1
)

REM Test 4: Backend .env
echo.
echo [4/8] Checking backend configuration...
if exist ".env" (
    echo    ✓ PASSED: .env file exists
    set /a TESTS_PASSED+=1
) else (
    echo    ❌ FAILED: .env file not found
    set /a TESTS_FAILED+=1
)

REM Test 5: Database
echo.
echo [5/8] Checking database file...
if exist "knowledge_base.db" (
    echo    ✓ PASSED: Database exists at backend/knowledge_base.db
    set /a TESTS_PASSED+=1
) else (
    echo    ⚠ WARNING: Database will be created on first backend startup
    set /a TESTS_PASSED+=1
)

cd ..

REM Test 6: Node.js
echo.
echo [6/8] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo    ⚠ WARNING: Node.js not found (frontend setup skipped)
    echo    Install from: https://nodejs.org
    set /a TESTS_FAILED+=1
) else (
    node --version
    echo    ✓ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 7: NPM Modules
echo.
echo [7/8] Checking frontend dependencies...
if exist "frontend\node_modules" (
    echo    ✓ PASSED: node_modules exists
    set /a TESTS_PASSED+=1
) else (
    echo    ⚠ WARNING: node_modules not found
    echo    Run: cd frontend ^&^& npm install
    set /a TESTS_FAILED+=1
)

REM Test 8: Frontend .env
echo.
echo [8/8] Checking frontend configuration...
if exist "frontend\.env" (
    echo    ✓ PASSED: Frontend .env exists
    set /a TESTS_PASSED+=1
) else (
    echo    ⚠ WARNING: Frontend .env not found
    echo    Creating default .env...
    (
        echo VITE_API_BASE_URL=http://localhost:8000/api/v1
    ) > frontend\.env
    set /a TESTS_PASSED+=1
)

REM Summary
echo.
echo ========================================
echo Summary
echo ========================================
echo Passed: %TESTS_PASSED%
echo Failed: %TESTS_FAILED%
echo ========================================
echo.

if %TESTS_FAILED% equ 0 (
    echo ✓ All checks passed! Ready to run.
    echo.
    echo Next steps:
    echo.
    echo 1. Terminal 1 - Backend:
    echo    cd backend
    echo    .\.venv\Scripts\Activate.ps1
    echo    uvicorn app.main:app --reload
    echo.
    echo 2. Terminal 2 - Frontend:
    echo    cd frontend
    echo    npm run dev
    echo.
    echo 3. Open browser: http://localhost:5173
    echo.
) else (
    echo ❌ Some checks failed. Please fix errors above.
    echo.
    echo For help, see: SETUP_GUIDE.md
    echo.
)

pause
