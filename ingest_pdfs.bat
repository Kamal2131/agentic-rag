@echo off
REM Batch script to ingest PDFs into vector database
REM Usage: ingest_pdfs.bat [directory_name]
REM Example: ingest_pdfs.bat raw_data1

SET DIR=%1
IF "%DIR%"=="" SET DIR=raw_data

echo ============================================================
echo PDF Ingestion for Agentic RAG
echo ============================================================
echo.
echo Directory: %DIR%
echo.

REM Check if Docker is running
docker ps >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    echo.
    pause
    exit /b 1
)

REM Check if containers are running
docker compose ps | findstr "agentic_rag_web" | findstr "running" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 🚀 Starting Docker containers...
    docker compose up -d
    echo ⏳ Waiting for services to be ready...
    timeout /t 40 /nobreak >nul
)

REM Run the ingestion using Django management command
echo 📚 Starting PDF ingestion...
echo.
docker compose exec web python manage.py ingest_pdfs %DIR%

echo.
echo ============================================================
echo Done!
echo ============================================================
pause
