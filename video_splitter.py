from asyncio.windows_events import NULL
import cv2

class Video_splitter:
    def __init__(self, video_to_capture = ''):
        self.capture = cv2.VideoCapture(video_to_capture)

        self.splited_video = []
        self.frames = 0

        self.split()
        
    def split(self):
        while(True):
            success, frame = self.capture.read()
 
            if success:
                self.splited_video.append(frame)
        
            else:
                break

            self.frames += 1 

    def get_frame(self, frame_no = 0):
        if frame_no > self.frames:
            return NULL
        else:
            return self.splited_video[frame_no]
        
    def get_count_frames(self):
        return self.frames