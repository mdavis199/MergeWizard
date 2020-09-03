@echo off
setlocal
pushd "%~dp0"
for /R "ui" %%a in (*.ui) do (
    echo %%a
    call :PROCESSUI %%a
)
endlocal
popd
goto :eof

:PROCESSUI
set filename=%~n1
set inpath=%~dp1
set outpath=%inpath:\ui\=\..\%
set outpath=%outpath%ui\
set output=%outpath%%filename%.py
if not exist "%outpath%" md "%outpath%"
python -m PyQt5.uic.pyuic "%1" -o "%output%"
goto :eof

