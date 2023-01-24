#!/bin/bash
OUTPUT_IMG=/home/pi/capture/$(date '+%Y%m%d%H%M%S').jpg;
RECENT_IMG=/home/pi/recent/most_recent.jpg;
sudo fswebcam --no-banner -d /dev/video0 -r 2304x1536 -s brightness=50% -p YUYV -S 60 -s backlight_compensation=1 -s sharpness=150 -s focus_auto=0 "$OUTPUT_IMG";
if [ -f "$RECENT_IMG" ]; then
  rm "$RECENT_IMG";
fi
echo "$OUTPUT_IMG"
echo "$RECENT_IMG"
if [ -f "$OUTPUT_IMG" ]; then
  ln "$OUTPUT_IMG" "$RECENT_IMG";
fi
