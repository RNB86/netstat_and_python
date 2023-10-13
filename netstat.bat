@echo off

reg query "HKU\S-1-5-19\Environment" >nul 2>&1
if '%errorlevel%' NEQ '0' (
    echo You must run the script as administrator
    echo Exiting now.
    pause
    exit
) 


setlocal EnableDelayedExpansion
set "path=\\doepker.local\Shares\it\Powerscripts\logs\"
set myname=""

FOR /F "tokens=* USEBACKQ" %%A IN (`hostname`) DO (
SET myname=%%A
)

set "logname=netstat_%myname%_%date%.log"
set "LogFile=%path%%logname%"
echo Log file name:
echo %logname%
echo Log path:
echo %LogFile%
echo Hold on. Report is in progress

if Exist "%LogFile%" del "%LogFile%"
echo.Protocol;SourceStack;DestinationStack;ConnectionState;PIDNumber;PIDName > %LogFile%


for /f "skip=4 tokens=1-5 delims= " %%A in ('netstat -ano') do call :netstat %%A %%B %%C %%D %%E
exit /b 0


:netstat
set protocol=%1
set srcStck=%2
set dstStck=%3
set state=%4
set pid_id=%5

if "%state%"=="" exit /b
if "%pid_id%"=="0" exit /b
if "%dstStck%"=="[::]:0" exit /b

if "%protocol%"=="UDP" (
    set state=NULL
    set pid_id=%4
)

for /f "skip=3 tokens=1 delims= " %%A in ('%SystemRoot%\System32\tasklist.exe /fi "pid eq %pid_id%"') do set "pid_name=%%A"
:: uncomment this to see the progress
:: echo %protocol%;%srcStck%;%dstStck%;%state%;%pid_id%;%pid_name%
echo %protocol%;%srcStck%;%dstStck%;%state%;%pid_id%;%pid_name% >> %LogFile%    
exit /b


echo Done.
:: uncomment this to see the report on screen
::pause
exit
