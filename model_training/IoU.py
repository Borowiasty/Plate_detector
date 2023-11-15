# import the necessary packages
import numpy as np
import cv2
import os
import time

from pathlib import Path
from ultralytics import YOLO

class bounding_box_setter:
	def __init__(self, str_from_file):
		self.from_file = str_from_file
		self.center = []
		self.size = []
		if (str_from_file.find('\n') == -1):
			self.one_line = True
		else: 
			self.one_line = False

		self._cut_string()
	
	def _cut_string(self):
		if(self.one_line):
			for i in range(2):
				self.center.append(float(self.from_file[:self.from_file.find(' ')]))
				self.from_file = self.from_file[self.from_file.find(' ') + 1:]
			for i in range(2):
				self.size.append(float(self.from_file[:self.from_file.find(' ')]))
				self.from_file = self.from_file[self.from_file.find(' ') + 1:]
	

	def de_normalizer(self, image):
		image_h, image_w, _ = image.shape
		self.center[0] = int(self.center[0] * image_w)
		self.center[1] = int(self.center[1] * image_h)

		self.size[0] = int(self.size[0] * image_w)
		self.size[1] = int(self.size[1] * image_h)
	
		self.bounding_box = []
		self.bounding_box.append(int(self.center[0] - 0.5 * self.size[0]))
		self.bounding_box.append(int(self.center[1] - 0.5 * self.size[1]))
		self.bounding_box.append(self.size[0])
		self.bounding_box.append(self.size[1])
		
model_name = 'dataset3_v2.pt'
path_of_yolo = os.path.dirname(__file__) + '\\ready_yolo_models\\' + model_name 
model = YOLO(path_of_yolo)



def bb_intersection_over_union(boxA, boxB):
	# determine the (x, y)-coordinates of the intersection rectangle
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
	yB = min(boxA[1] + boxA[3], boxA[1] + boxB[3])
	
	# compute the area of intersection rectangle
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
	
	# compute the area of both the prediction and ground-truth
	# rectangles
	boxAArea = abs((boxA[0] + boxA[2] - boxA[0] + 1) * (boxA[1] + boxA[3] - boxA[1] + 1))
	boxBArea = abs((boxB[0] + boxB[2] - boxB[0] + 1) * (boxA[1] + boxB[3] - boxB[1] + 1))
	
	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	iou = interArea / float(boxAArea + boxBArea - interArea)
	
	# return the intersection over union value
	return iou

counter = 0
mean = 0.0
time_of_start = time.time()
for p in Path('.').glob('**/dataset_1/test/**/*.jpg'):
	image_path = str(p)
	ground_truth = str(p)
	ground_truth_path = ground_truth[:ground_truth.find('images')] + 'labels' + ground_truth[ground_truth.find('images')+6:-3] + 'txt'

	if(os.path.isfile(image_path) and os.path.isfile(ground_truth_path)):
		image_file = cv2.imread(image_path)
		
		ground_truth_file = open(ground_truth_path, 'r')

		ground_truth_from_file = ground_truth_file.read()
		if(ground_truth_from_file.find('\n') == -1):
			ground_truth_from_file = ground_truth_from_file[2:]
				
			curr_bounding = bounding_box_setter(ground_truth_from_file)
			curr_bounding.de_normalizer(image_file)
			
			results = model.predict(source = image_path, show = False,  verbose=False)         # YOLO prediction
			for result in results:
				boxes = result.boxes.cpu().numpy()
				for box in boxes:
					r = box.xywh[0].astype(int)

					cv2.rectangle(image_file, curr_bounding.bounding_box, (0, 255, 0), 2)
					cv2.rectangle(image_file, [int(r[0]-0.5*r[2]), int(r[1]-0.5*r[3]), r[2], r[3]] , (255, 0, 0), 2)

					# compute the intersection over union and display it
					iou = bb_intersection_over_union(curr_bounding.bounding_box, [int(r[0]-0.5*r[2]), int(r[1]-0.5*r[3]), r[2], r[3]])
					counter = counter + 1
					mean = mean + iou
					cv2.putText(image_file, "IoU: {:.4f}".format(iou), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
					#print("{}: {:.4f}".format(image_path, iou))

					#cv2.imshow("Image", image_file)
					#cv2.waitKey(0)
time_of_end = time.time()

mean = mean / counter

print("\n-----  ", model_name, "  -----")
print("Mean UoI: ", mean)
print("Working time: ", time_of_end-time_of_start, "\n")