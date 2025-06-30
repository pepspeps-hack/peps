@echo off
echo Starting LuxeWatch Emporium Server...

REM Change directory to the 'app' folder where main.py is located
cd app

echo Launching Flask application...
REM Run the Flask application
REM Assumes python is in PATH. Use py -m flask run or python3 if needed.
python main.py

echo Server stopped.
pause
