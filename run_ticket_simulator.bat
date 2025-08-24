@echo off
echo ========================================
echo   EventPro Ticket Booking Simulator
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install required packages
echo Installing required packages...
pip install -r simulator_requirements.txt

:: Run the simulator
echo.
echo Starting Ticket Booking Simulator...
echo.
python ticket_booking_simulator.py

echo.
echo Simulator finished. Press any key to exit...
pause