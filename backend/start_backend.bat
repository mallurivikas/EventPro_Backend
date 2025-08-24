@echo off
echo Starting Event Analytics Dashboard Backend...
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Start Flask server
echo.
echo Starting Flask server...
echo Backend will be available at: http://localhost:5000
echo.
python app.py

pause