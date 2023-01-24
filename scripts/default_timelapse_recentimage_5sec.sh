#!/bin/bash
# defaults
OUTPUT_IMG=/home/pi/capture/$(date '+%Y%m%d%H%M%S').jpg;
RECENT_IMG=/home/pi/recent/most_recent.jpg;

# use while loop to control caputure rate
while true; do
  # capture
  #sudo fswebcam --no-banner -d /dev/video0 -r 2304x1536 -s brightness=50% -p YUYV -S 60 -s backlight_compensation=1 -s sharpness=150 -s focus_auto=0 "$OUTPUT_IMG";
  sudo fswebcam -d /dev/video0 -r 2304x1536 -s brightness=50% -p YUYV -s backlight_compensation=1 -s sharpness=150 -s focus_auto=1 "$OUTPUT_IMG";

  # plaace freshly captured image in 'recent' dir
  if [ -f "$RECENT_IMG" ]; then
    rm -f "$RECENT_IMG";
  fi
  echo "$OUTPUT_IMG"
  echo "$RECENT_IMG"
  if [ -f "$OUTPUT_IMG" ]; then
    ln "$OUTPUT_IMG" "$RECENT_IMG";
  fi

  # sleep
  sleep 5;
done
