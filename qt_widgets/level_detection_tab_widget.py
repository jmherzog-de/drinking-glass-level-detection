import cv2
from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox
from .image_widget import ImageWidget
import numpy as np


class LevelDetectionTabWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.central_layout = QHBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        self.groupbbox_contours = QGroupBox()
        self.groupbbox_contours.setObjectName(u"groupbox_contours")
        self.groupbbox_contours.setTitle(u"Contours")
        self.groupbbox_contours_layout = QHBoxLayout(self.groupbbox_contours)
        self.groupbbox_contours_layout.setObjectName(u"groupbox_contours_layout")

        self.contours_image_widget = ImageWidget()
        self.contours_image_widget.setObjectName(u"contours_image_widget")
        self.groupbbox_contours_layout.addWidget(self.contours_image_widget)
        self.central_layout.addWidget(self.groupbbox_contours)

    def __contours_image(self, frame: np.ndarray):
        kernel = np.ones((5, 5), np.uint8)
        frame = cv2.erode(frame, kernel, 2)
        frame = cv2.dilate(frame, kernel, 3)
        # frame = cv2.Canny(frame, 30, 150)
        # frame = cv2.dilate(frame, np.ones((5, 5), np.uint8), 8)
        # frame = cv2.Sobel(frame, cv2.CV_8U, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        # frame = cv2.dilate(frame, kernel, 3)
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        for cnt in contours:
            cnt_area = cv2.contourArea(cnt)
            if cnt_area > 450:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
        self.contours_image_widget.update_image(frame)

    def update_image(self, diff_frame: np.ndarray):
        self.__contours_image(diff_frame.copy())
