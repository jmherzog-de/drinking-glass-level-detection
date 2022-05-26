import time

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal


class VideoPlayer(QThread):

    update_frame = Signal(np.ndarray)

    def __init__(self):
        QThread.__init__(self, parent=None)
        self.play = False
        self.__cap = None
        self.status = True
        self.video_file_path = "capture.mp4"

    def run(self):
        self.__cap = cv2.VideoCapture(self.video_file_path)

        while self.__cap.isOpened():
            ret, frame = self.__cap.read()
            if not ret:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.update_frame.emit(frame)
            time.sleep(0.05)
