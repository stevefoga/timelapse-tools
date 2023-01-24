#!/bin/bash
sudo fswebcam --no-banner -d /dev/video0 /home/pi/capture/%Y%m%d%H%M%S.jpg -r 2304x1536 -s brightness=50% -p YUYV -S 60 -s backlight_compensation=1 -s sharpness=150 -s focus_auto=0
