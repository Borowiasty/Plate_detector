import os
import time
import datetime
import cv2
import easyocr
import threading
import torch

from ultralytics import YOLO
from pathlib import Path

import Video_splitter
import Video

print("Using GPU: ", torch.cuda.get_device_name(torch.cuda.current_device()))

# setting model of YOLOv8 alorithm
model = YOLO('custom_yolov8.pt')                                                                                              

# static camera seting
camera_width = 640
camera_height = 384
frames_per_sec_for_camera = 60

# setting easyOCR reader parameters
reader = easyocr.Reader(['en'], gpu = True)

# video source, change operatring mode value for live 0, and from-local-macheinee 1

cur_frame_no = -1
time.sleep(1)

# mian loop
for p in Path('.').glob('**/testing_images/*.jpg'):

    image_path = str(p)
    cur_image = cv2.imread(image_path)
    
    results = model.predict(source = cur_image, show = True, vid_stride = frames_per_sec_for_camera, verbose=False)                         # YOLO prediction
    #results = model.track(source = cur_image, show = True, vid_stride = frames_per_sec_for_camera, verbose=False, persist= True)           # YOLO tracking [TODO]



    for result in results:                                                                                                  # operating in reasults from YOLO
        boxes = result.boxes.cpu().numpy()                                                                                  # get boxes on cpu in numpy
        for box in boxes:                                                                                                   # iterate boxes
            r = box.xyxy[0].astype(int)                                                                                     # get corner points as int
            img = cur_image[r[1]:r[3], r[0]:r[2]]                                                                           # cut out interesting box
            
            
            filename = str(datetime.datetime.now())                                                                         # can save detected plate do file
            filename = filename.replace(' ', '_')
            filename = filename.replace(':','-')
            filename = filename.replace('.','-')
            filename = os.path.dirname(__file__) + '\\cut_out_plates\\' + filename + '.png'
            cv2.imwrite(filename, img)

cv2.destroyAllWindows()