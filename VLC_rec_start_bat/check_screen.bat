@echo off 
:: 2019/08/01
echo :: 録画範囲の確認用VLCを起動
set screen_top=%1
set screen_left=%2
set rec_area_width=%3
set rec_area_height=%4

echo :: 原点からの距離 px
echo :: top = %screen_top%, left = %screen_left%

echo :: 録画範囲
echo :: %rec_area_width%, %rec_area_height%

"C:\Program Files\VideoLAN\VLC\vlc" screen:// ^
:screen-fps=30 ^
:screen-top=%screen_top% ^
:screen-left=%screen_left% ^
:screen-width=%rec_area_width% ^
:screen-height=%rec_area_height% ^

timeout 10
exit
