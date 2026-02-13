@echo off
cd /d "%~dp0"
title Export my emails
echo.
echo ----------------------------------------
echo   Exporting your last 10 Gmail emails
echo ----------------------------------------
echo.

echo Installing/checking dependencies (one-time, may take a moment)...
py -3 -m pip install -q -r requirements.txt 2>nul || python -m pip install -q -r requirements.txt 2>nul || pip install -q -r requirements.txt
echo.

echo When the browser opens, sign in with YOUR Gmail and click Allow.
echo Then come back here and wait for "Done".
echo.
pause

py -3 fetch_last_10_full.py 2>nul || python fetch_last_10_full.py
if errorlevel 1 (
    echo.
    echo Something went wrong. Check the message above.
    echo If you see "Python is not recognized", install Python first (see CLIENT_INSTRUCTIONS).
    echo Otherwise, take a screenshot and send it to Mahmoud.
) else (
    echo.
    echo ----------------------------------------
    echo   Look for this file in this folder:
    echo   last_10_emails_full.json
    echo   Send that file to Mahmoud.
    echo ----------------------------------------
)

echo.
pause
