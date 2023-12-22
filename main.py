'''
    Main of program designed to recognize license plates in real time, made for Poznan Univeristy of Technology sem project
'''

import os
import time
import datetime
import cv2
import easyocr
import threading

from ultralytics import YOLO

import Video_splitter
import Video
import Plates_table
import tensorflow as tf
print(len(tf.config.experimental.list_physical_devices('GPU')))

# setting model of YOLOv8 alorithm
model = YOLO('custom_yolov8.pt')
# delcaring var for possible exit
quit_cam = 0                                                                                                

#creating lock for local database multithread
lock = threading.Lock()

# creating local in code database
local_plates_databe = Plates_table.Plates_local_databe()                                                                # working mode
#local_plates_databe = Plates_table.Plates_local_databe(show = 1)                                                           # debugging mode (show readed text)
#local_plates_databe = Plates_table.Plates_local_databe(show = 2)                                                           # debugging mode (show postprocessed number of plate)

# static camera seting
camera_width = 640
camera_height = 384
frames_per_sec_for_camera = 60

# setting easyOCR reader parameters
reader = easyocr.Reader(['en'], gpu = True)

# video source, change operatring mode value for live 0, and from-local-macheinee 1
operating_mode = 1
from_file_source = 'side_1.mp4'

from_file_source = os.path.dirname(__file__) + '\\testing_video\\' + from_file_source
video_stream = Video.Camera_stream((camera_width, camera_height), frames_per_sec_for_camera, 0).start()                     # operating_mode = 0
static_video = Video_splitter.Video_splitter(from_file_source)                                                              # operating_mode = 1
cur_frame_no = -1
time.sleep(1)

# mian loop
while quit_cam == 0:
    time.sleep(1/frames_per_sec_for_camera)                                                                                 # setting framerate

    # based on selected operating mode
    if operating_mode == 0:                                                                                                 # live mode
        cur_image = video_stream.read() 
    else:                                                                                                                   # video mode
        cur_frame_no += 1

        if cur_frame_no < static_video.get_count_frames():
            try:
                cur_image = static_video.get_frame(cur_frame_no)
            except:
                print('Index out of bound for video, emergency exit')
                cv2.destroyAllWindows()
                video_stream.stop()
                quit(1)
        else:
            cv2.destroyAllWindows()
            video_stream.stop()
            print("End of video")
            quit(0)
    
    results = model.predict(source = cur_image, show = True, vid_stride = frames_per_sec_for_camera, verbose=False)         # YOLO prediction
    #results = model.track(source = cur_image, show = True, vid_stride = frames_per_sec_for_camera, verbose=False, persist= True)         # YOLO tracking [TODO]



    for result in results:                                                                                                  # operating in reasults from YOLO
        boxes = result.boxes.cpu().numpy()                                                                                  # get boxes on cpu in numpy
        for box in boxes:                                                                                                   # iterate boxes
            r = box.xyxy[0].astype(int)                                                                                     # get corner points as int
            img = cur_image[r[1]:r[3], r[0]:r[2]]                                                                           # cut out interesting box
            
            '''
            filename = str(datetime.datetime.now())                                                                         # can save detected plate do file
            filename = filename.replace(' ', '_')
            filename = filename.replace(':','-')
            filename = filename.replace('.','-')
            filename = os.path.dirname(__file__) + '\\cut_out_plates\\' + filename + '.png'
            cv2.imwrite(filename, img)
            '''
            
            #cv2.imshow('frame',img)                                                                                        # can show currently operated frame
            
            result = reader.readtext(img)                                                                                   # reading text in images

            text = ''

            for res in result:                                                                                              # getting text readed by easyOCR
                if len(result) == 1:
                    text = res[1]
                
                if len(result) > 1 and len(res[1]) > 6 and res[2] > 0.7:
                    text = res[1]
            local_plates_databe.add_plate(text)
            
                

    if cv2.waitKey(5) & 0xFF == ord('q'):
        quit_cam = 1

local_plates_databe.print_plates()
cv2.destroyAllWindows()
video_stream.stop()