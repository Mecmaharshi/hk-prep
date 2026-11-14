@echo off
rem Lets Windows users type  .\hk run  from PowerShell or cmd. It runs the real script (hk) in Git Bash.
setlocal
set "BASH="
if exist "%ProgramFiles%\Git\bin\bash.exe" set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not defined BASH if exist "%LocalAppData%\Programs\Git\bin\bash.exe" set "BASH=%LocalAppData%\Programs\Git\bin\bash.exe"
if not defined BASH if exist "%ProgramFiles(x86)%\Git\bin\bash.exe" set "BASH=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not defined BASH (
  echo hk: Git Bash not found. Install Git for Windows: https://git-scm.com
  exit /b 1
)
set "HERE=%~dp0"
"%BASH%" "%HERE:\=/%hk" %*
exit /b %ERRORLEVEL%
