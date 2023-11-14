import Video_splitter
import Video
import cv2
import time
import os
import datetime

from_file_source = 'side_1.mp4'
from_file_source = os.path.dirname(__file__) + '\\' + from_file_source

static_video = Video_splitter.Video_splitter(from_file_source)  

cur_frame_no = -1

# delcaring var for possible exit
quit_cam = 0

time.sleep(1)

while quit_cam == 0:                                                                         
    cur_frame_no += 1
    if cur_frame_no < static_video.get_count_frames():
        try:
            cur_image = static_video.get_frame(cur_frame_no)
            if cur_frame_no % 20 == 0:
                filename = str(datetime.datetime.now())                                                                         # can save detected plate do file
                filename = filename.replace(' ', '_')
                filename = filename.replace(':','-')
                filename = filename.replace('.','-')
                filename = os.path.dirname(__file__) + '\\cut_frames\\' + filename + '.png'
                cv2.imwrite(filename, cur_image)
        except:
            print('Index out of bound for video, emergency exit')
            quit(1)
    else:
        break

print("Done")