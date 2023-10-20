'''
    Use this file ONLY when you want your model to be trained, this file will train new model, also will be working for aproxima 1 - 2 hours
'''

from ultralytics import YOLO

model = YOLO('custom_yolov8_model.pt')

model.train(data='car_license_plate.v1i.yolov8/data.yaml', epochs=120, imgsz=640)

