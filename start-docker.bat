@echo off
echo 🐳 Starting Coin Flip Simulation with Docker
echo =============================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is required but not installed.
    echo Please install Docker and try again.
    echo Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is required but not installed.
    echo Please install Docker Compose and try again.
    echo Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose found
echo.

REM Check if Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker daemon is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker daemon is running
echo.

echo 🚀 Building and starting services...
echo This may take a few minutes on first run...
echo.

REM Build and start services
docker-compose up --build

echo.
echo 🎉 Application should now be running!
echo 📱 Open your browser and go to: http://localhost:8080
echo.
echo To stop the application, press Ctrl+C
pause

