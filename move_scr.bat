FOR /F "tokens=*" %%i in ('type %~dp0\.env') do SET %%i
%~dp0\venv\Scripts\python %~dp0\move_scr.py
pause