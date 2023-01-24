Scirpts used to execute various processes on timelapse capture device.  

## Notes
Reset focus on camera:
```
sudo v4l2-ctl -d /dev/video0 -c exposure_auto=1
```
