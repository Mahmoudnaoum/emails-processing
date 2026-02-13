@echo off
cd /d "%~dp0"
title Export my emails (~1000)
echo.
echo ----------------------------------------
echo   Exporting your last ~1000 Gmail emails
echo   (This can take a few minutes)
echo ----------------------------------------
echo.

echo Installing/checking dependencies (one-time)...
py -3 -m pip install -q -r requirements.txt 2>nul || python -m pip install -q -r requirements.txt 2>nul || pip install -q -r requirements.txt
echo.

echo When the browser opens, sign in with YOUR Gmail and click Allow.
echo Then come back here and wait - fetching 1000 emails takes a few minutes.
echo.
pause

py -3 fetch_last_1000_full.py 2>nul || python fetch_last_1000_full.py
if errorlevel 1 (
    echo.
    echo Something went wrong. Check the message above.
    echo Take a screenshot and send it to Mahmoud if needed.
) else (
    echo.
    echo ----------------------------------------
    echo   Look for this file in this folder:
    echo   last_1000_emails_full.json
    echo   Send that file to Mahmoud.
    echo ----------------------------------------
)

echo.
pause
