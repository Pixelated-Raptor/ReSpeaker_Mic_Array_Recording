#!/bin/bash

rclone copy Jetson:/home/user/Code/ReSpeaker_Mic_Array_Recording/Recs ./Recs
rclone copy Jetson:/home/user/Code/ReSpeaker_Mic_Array_Recording/Logs ./Logs
#rclone copy --progress Orin:/home/user/Code/Mic/Recs ./Recs
#rclone copy --progress Orin:/home/user/Code/Mic/Logs ./Logs
