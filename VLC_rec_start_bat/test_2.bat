@echo off 

:: ƒpƒ‰ƒƒ^ó‚¯æ‚è
set %%rec_seconds=%1
set %%rec_double_seconds=%2
set %%screen_top=%3
set %%screen_left=%4
set %%rec_area_width=%5
set %%rec_area_height=%6
set %%movie_format_width=%7
set %%movie_format_height=%8

:: ‘˜^‰æ•b”
set /a rec_total_seconds=%rec_seconds%+%rec_double_seconds%


:: “úƒZƒbƒg
set dt=%date%
set tm=%time%

set year=%dt:~0,4%
set month=%dt:~5,2%
set day=%dt:~8,2%

set hour=%tm:~0,2%
set minute=%tm:~3,2%
set second=%tm:~6,2%
set msecond=%tm:~9,2%

:: ƒtƒ@ƒCƒ‹–¼
set dtime=%year%%month%%day%_%hour%%minute%
set fname=%dtime%.mp4


echo :: ˜^‰æƒpƒ‰ƒ[ƒ^[
echo :: ˜^‰æ•b”  = %rec_seconds% •b
echo :: d•¡•b”  = %rec_double_seconds% •b
echo :: ‘˜^‰æ•b”= %rec_total_seconds% •b
echo :: Œ´“_‚©‚ç‚Ì‹——£ px
echo :: top = %screen_top%, left = %screen_left%

echo :: ˜^‰æ”ÍˆÍ
echo :: %rec_area_width%, %rec_area_height%

echo :: “®‰æ‰ğ‘œ“x
echo :: %movie_format_width%, %movie_format_height%


"C:\Program Files\VideoLAN\VLC\vlc" -I dummy screen:// ^
:run-time=%rec_total_seconds% ^
:screen-fps=30 ^
:screen-left=0 ^
:screen-top=1920 ^
:screen-width=%rec_area_width% ^
:screen-height=%rec_area_height% ^
--sout=#^
transcode{vcodec=h264,acodec=none,width=%rec_format_width%,height=%rec_format_height%}^
:standard{access=file,mux=mp4,dst=%fname%} vlc://quit


timeout 3 
exit 
