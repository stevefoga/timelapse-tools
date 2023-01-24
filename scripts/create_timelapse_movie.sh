#!/bin/bash
cd $1
first_image=(*)
first_image_number="${first_image%.*}"
creation_date=$(date +%Y%m%d%k%M%S)
movie_ext=".mp4"
ffmpeg -r 30 -start_number $first_image_number -i %14d.jpg -vcodec libx264 "$creation_date$movie_ext"
