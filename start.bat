@echo off
REM ACUR Embedding Service Startup Script (Windows)
REM This script starts the embedding service with all-MiniLM-L6-v2 model

echo ===============================================
echo ACUR Embedding Service
echo Model: all-MiniLM-L6-v2 from HuggingFace
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [2/3] Checking dependencies...
python -c "import sentence_transformers" 2>nul
if errorlevel 1 (
    echo [WARNING] sentence-transformers not found. Installing...
    pip install -r requirements.txt
)

REM Start the service
echo [3/3] Starting embedding service...
echo.
echo Service will start on: http://localhost:8000
echo.
echo Note: First startup will download the model from HuggingFace
echo       This is a one-time ~80MB download.
echo.
echo Press Ctrl+C to stop the service
echo ===============================================
echo.

uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --reload
