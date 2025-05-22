@echo on
echo Starting Authentication Server...
cd %~dp0
:: Use global Python installation instead of virtual environment
python run_server.py
if %ERRORLEVEL% NEQ 0 (
    echo Error starting server. Check for errors above.
    pause
) else (
    echo Server started successfully.
    pause
)
