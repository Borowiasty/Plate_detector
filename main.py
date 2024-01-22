'''
    Main of program designed to recognize license plates in real time, made for Poznan Univeristy of Technology sem project
'''

import os
import time
import cv2
import threading
import torch

from ultralytics import YOLO

import Video_splitter
import Video
import Plates_table
import TrOCR_reader
import Db_connector

print("Using GPU: ", torch.cuda.get_device_name(torch.cuda.current_device()))

# setting model of YOLOv8 alorithm
model = YOLO('custom_yolov8.pt')
# delcaring var for possible exit
quit_cam = 0                                                                                                

#creating lock for local database multithread
lock = threading.Lock()

# creating local in code database
local_plates_database = Plates_table.Plates_local_databe(lock)                                                                # working mode
#local_plates_database = Plates_table.Plates_local_databe(show = 1)                                                           # debugging mode (show readed text)
#local_plates_database = Plates_table.Plates_local_databe(lock, show = 2)                                                     # debugging mode (show postprocessed number of plate)

#creating database connection
database = Db_connector.Db_connector("localhost", "root", "root", "plate_detector", lock)
database.start_db_supervison(local_plates_database)
if not database.is_connected:
    print("Database connection error")
    quit(1)

# static camera seting
camera_width = 640
camera_height = 384
frames_per_sec_for_camera = 60

# setting reader
#model_size = 'small'
model_size = 'large'
whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
reader = TrOCR_reader.TrOCR_reader_class(model_size = model_size, whitelist = whitelist)

# video source, change operatring mode value for live 0, and from-local-macheinee 1
operating_mode = 1
from_file_source = 'side.mp4'

side_GT = ['PO1RU65', 'PY32166', 'PZ8990W', 'WE5F183', 'PO3152E', 'PO6505H', 'PO4RR98', 'PO5NY07', 'PO6HX56', 'PY22520', 'PO392RF', 'EL331VR', 'PJARU55', 'PO697FV', 'PO189CT', 'PKR55619', 'PO9362F', 'PO364PS', 'PO7RV44', 'PO178UH', 'PO445LE', 'PO6LX99', 'PO2XU12', 'POS02563', 'PO9S177', 'PGN871CS']

from_file_source = os.path.dirname(__file__) + '\\testing_video\\' + from_file_source
video_stream = Video.Camera_stream((camera_width, camera_height), frames_per_sec_for_camera, 0).start()                     # operating_mode = 0
static_video = Video_splitter.Video_splitter(from_file_source)                                                              # operating_mode = 1
image_list = os.path.dirname(__file__) + '\\testing_images' 
cur_frame_no = -1
res_num = 0
res_sum = 0
time.sleep(1)

# mian loop
time_of_start = time.time()
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
            break
    if cur_frame_no % 5 == 0:
        results = model.predict(source = cur_image, show = True, vid_stride = frames_per_sec_for_camera, verbose=False)         # YOLO prediction

        for result in results:                                                                                                  # operating in reasults from YOLO
            boxes = result.boxes.cpu().numpy()                                                                                  # get boxes on cpu in numpy
            for box in boxes:                                                                                                   # iterate boxes
                r = box.xyxy[0].astype(int)                                                                                     # get corner points as int
                img = cur_image[r[1]:r[3], r[0]:r[2]]                                                                           # cut out interesting box
                
                #cv2.imshow('frame',img)                                                                                        # can show currently operated frame

                resolution = float(len(img[0]) / len(img))
                res_num += 1
                res_sum += resolution
                if resolution >= 4 and resolution <= 4.9:
                    result = reader.text_from_image(img)                                                                        # reading text in images

                    text = result[0]

                    local_plates_database.add_plate(text)

    if cur_frame_no % 100 == 0 and cur_frame_no > 1:
        database.synchronize = True
                

    if cv2.waitKey(5) & 0xFF == ord('q'):
        quit_cam = 1

time_of_end = time.time()
database.synchronize = True

while len(local_plates_database.get_local_plates()) > 0:
    time.sleep(1)

local_plates_database.print_plates()
local_plates_database.print_plates_backup()
TP = 0
FP = 0
FN = 0
once_upon_a_time_there_was_a_plate = []
for plate in local_plates_database.get_local_plates_backup():
    if plate in side_GT:
        once_upon_a_time_there_was_a_plate.append(plate)
        TP += 1
    else:
        FP += 1

for plate in side_GT:
    if plate in once_upon_a_time_there_was_a_plate:
        continue
    else:
        FN += 1

print("All plates: ", len(side_GT))
print("All detected plates: ", len(local_plates_database.get_local_plates_backup()))
print("Positive detected plates: ", TP)
print("Plates detected but don't exist: ", FP)
print("Plates undetected: ", FN)

print("Time: ", str((time_of_end-time_of_start)))
print("Mean fps: ", str(float(static_video.get_count_frames()/(time_of_end-time_of_start))))

print(res_sum/res_num)
cv2.destroyAllWindows()
video_stream.stop()
database.stop_db_supervisor()