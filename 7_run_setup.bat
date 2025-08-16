@echo off
title Enhanced College Extension - Quick Setup
color 0A
echo.
echo ================================================================
echo    ENHANCED COLLEGE EXTENSION APPLICATION - QUICK SETUP
echo ================================================================
echo.
echo This will set up the enhanced version with:
echo   * Modern full-screen GUI
echo   * Enter key support for data submission
echo   * Auto CSV export on every data entry
echo   * Real-time activity monitoring
echo.
echo ================================================================
echo.

echo Step 1: Setting up database...
python 1_setup_database.py
echo.

echo Database setup completed!
echo.
echo Next steps:
echo 1. Start enhanced server: python enhanced_server.py
echo 2. Run enhanced client: python enhanced_client_gui.py
echo.
echo Or create executables: python enhanced_deployment.py
echo.
echo ================================================================
echo Enhanced setup completed! Enjoy the new features!
echo ================================================================
pause
