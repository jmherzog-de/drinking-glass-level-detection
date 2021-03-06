import time
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal


class VideoPlayer(QThread):
    """
    Video player with Qt based QThread usage.
    """

    # Callback signal on new frame available
    update_frame = Signal(np.ndarray)

    def __init__(self):
        """
        Constructor.
        """

        QThread.__init__(self, parent=None)
        self.play = False
        self.__cap = None
        self.status = True
        self.video_file_path = "capture.mp4"

    def run(self):
        """
        Capture video and save on local disk.
        :return: None
        """
        self.__cap = cv2.VideoCapture(self.video_file_path)
        self.play = True
        
        while self.__cap.isOpened() and self.play:
            ret, frame = self.__cap.read()
            if not ret:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.update_frame.emit(frame)
            time.sleep(0.05)
