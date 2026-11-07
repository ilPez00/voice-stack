@echo off
rem Requires Windows SDK signtool and a code signing cert (PFX).
rem Usage: sign_windows.bat path\to\exe "Your Cert Subject" C:\path\cert.pfx password
setlocal
set FILE=%1
set SUBJECT=%2
set PFX=%3
set PASS=%4
signtool sign /f "%PFX%" /p "%PASS%" /tr http://timestamp.digicert.com /td sha256 /fd sha256 "%FILE%"
echo Signed: %FILE%
