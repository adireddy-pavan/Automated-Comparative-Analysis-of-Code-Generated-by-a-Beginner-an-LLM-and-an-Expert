@echo off
setlocal
cd /d "%~dp0"
echo === THARUN WINDOWS EVIDENCE VERIFICATION ===
echo The original project is preserved. Results will be saved in verification\windows_runs.
echo.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_WINDOWS_AND_SAVE.ps1"
set "CODE=%ERRORLEVEL%"
echo.
echo Runner exit status: %CODE%
echo Please send back the RESULTS_*.zip from verification\windows_runs.
echo If failed, send the FAILED results too. Never delete failures.
pause
exit /b %CODE%
