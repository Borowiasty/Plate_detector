from ultralytics import YOLO
from ultralytics.yolo.v8.detect.predict import DetectionPredictor
import Video
import time
import cv2
import easyocr

model = YOLO('yolov8n.pt')

quit_cam = 0

# static camera seting
camera_width = 640
camera_height = 384
frames_per_sec_for_camera = 1

reader = easyocr.Reader(['en'], gpu = True)

video_stream = Video.Camera_stream((camera_width, camera_height), frames_per_sec_for_camera, 0).start()
time.sleep(1)

while quit_cam == 0:
    time.sleep(1/frames_per_sec_for_camera)
    cur_image = video_stream.read() 
    results = model.predict(source = cur_image, show = True)

    for result in results:
        boxes = result.boxes.cpu().numpy()                         # get boxes on cpu in numpy
        for box in boxes:                                          # iterate boxes
            r = box.xyxy[0].astype(int)                            # get corner points as int
            #print(r)                                               # print boxes
            img = cur_image[r[1]:r[3], r[0]:r[2]]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            #cv2.imshow('klatka',img)
            

    #check if 'e' key is pressed, if so exit mian loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord('e'):
        quit_cam = 1

cv2.destroyAllWindows()
video_stream.stop()