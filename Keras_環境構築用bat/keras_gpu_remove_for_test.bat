@echo off

set env_name=keras-gpu

echo :: conda %env_name% remove

echo y | call conda remove -n %env_name% --all

echo :: conda %env_name% remove complete

pause
