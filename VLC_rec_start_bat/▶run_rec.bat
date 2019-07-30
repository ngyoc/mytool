::  2019/07/30
@echo off
::
::  実行開始する時刻（分）
    set interval_min=30
    set list_start_min=(00 30)
::
::  録画する秒数
    set rec_seconds=1800
::
::  録画を重複させる秒数
  set rec_double_seconds=60
::
::  録画範囲
::    幅    1920  3840  5760  7680  9600
    set rec_area_width=1920
::    高さ  1080  2160  3240  4320  5400
    set rec_area_height=1080
::
::  録画範囲原点
    set screen_top=0
    set screen_left=0
::
::
::  動画解像度
::    幅
    set movie_format_width=1920
::    高さ
    set movie_format_height=1080
::
::  管理用 変更しないでください
    set loop_sec=10
    set cooltime=60
    set flag_firsttime=1
::
::
    md .\rec
::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:check_start_min
::
    set dt=%date%
    set tm=%time: =0%
::
    set year=%dt:~0,4%
    set month=%dt:~5,2%
    set day=%dt:~8,2%
::
    set hour=%tm:~0,2%
    set minute=%tm:~3,2%
    set second=%tm:~6,2%
    set msecond=%tm:~9,2%
::
::
::
    call  :sub_func  %minute%
    echo ERRORLEVEL=%ERRORLEVEL%
    set onetime_rec_seconds=%ERRORLEVEL%
    echo onetime_rec_seconds=%onetime_rec_seconds%
::
if %flag_firsttime% EQU 1 (
    echo first time
    echo onetime_rec_seconds=%onetime_rec_seconds%
    start /MIN rec.bat %onetime_rec_seconds% %rec_double_seconds% %screen_top% %screen_left% %rec_area_width% %rec_area_height% %movie_format_width% %movie_format_height%
    set flag_firsttime=0
    timeout %cooltime%
    echo flag_firsttime=%flag_firsttime%
goto check_start_min
) else (
for %%i in %list_start_min% do ^
if %%i EQU %minute% (
    echo %%i, %minute%, cooltime = %cooltime%
    start /MIN rec.bat %rec_seconds% %rec_double_seconds% %screen_top% %screen_left% %rec_area_width% %rec_area_height% %movie_format_width% %movie_format_height%
    timeout %cooltime%
)
    timeout %loop_sec%
goto check_start_min
)
  exit  /B
exit  /B
::
:sub_func
::
  set /a zzz_sub_func=60 * ((160 + %interval_min% - 1%1) %% %interval_min%)
  echo  zzz_sub_func=%zzz_sub_func%
  exit  /B  %zzz_sub_func%
::
exit  /B  %zzz_sub_func%
::
pause
