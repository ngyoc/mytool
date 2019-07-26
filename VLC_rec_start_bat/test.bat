@echo off


:: ÀsŠJn‚·‚éi•ªj
set list_start_min=(00 05 10 15 20 25 30 35 40 45 50 55)

:: ˜^‰æ‚·‚é•b”
set rec_seconds=300

:: ˜^‰æ‚ğd•¡‚³‚¹‚é•b”
set rec_double_seconds=10




:: ˜^‰æ”ÍˆÍ
::   •
set rec_area_width=1920
::   ‚‚³
set rec_area_height=1080


:: “®‰æ‰ğ‘œ“x
::   •
set movie_format_width=1920
::   ‚‚³
set movie_format_height=1080


:: ˜^‰æ”ÍˆÍŒ´“_
set screen_top=0
set screen_left=0





:: ŠÇ——p
set loop_sec=10
set cooltime=60

set flag_firsttime=1









:check_start_min

set dt=%date%
set tm=%time%

set year=%dt:~0,4%
set month=%dt:~5,2%
set day=%dt:~8,2%

set hour=%tm:~0,2%
set minute=%tm:~3,2%
set second=%tm:~6,2%
set msecond=%tm:~9,2%

:: set dtime=%year%%month%%day%_%hour%%minute%%second%



if %flag_firsttime% EQU 1 (

echo :: first time &^
REM set /a onetime_rec_seconds=%rec_seconds%-(%minute%*60+%second%) &^
REM echo onetime_rec_seconds = %rec_seconds%, cooltime = %cooltime% &^
start test_2.bat %rec_seconds% %rec_double_seconds% %screen_top% %screen_left% %rec_area_width% %rec_area_height% %movie_format_width% %movie_format_height% &^
timeout %cooltime% &^
set flag_firsttime=0 &^
echo flag_firsttime=%flag_firsttime% &^
goto check_start_min

) else (

for %%i in %list_start_min% do ^
if %%i EQU %minute% (
echo %%i, %minute%, cooltime = %cooltime% &^
start test_2.bat %rec_seconds% %rec_double_seconds% %screen_top% %screen_left% %rec_area_width% %rec_area_height% %movie_format_width% %movie_format_height% &^
timeout %cooltime%
)
timeout %loop_sec%

goto check_start_min

)


pause

