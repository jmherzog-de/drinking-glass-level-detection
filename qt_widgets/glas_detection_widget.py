from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox
from .image_widget import ImageWidget
import cv2
import numpy as np
import bv_algorithms as bv


class GlasDetectionTabWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.__glas_detector = bv.GlasDetection()

        self.glas_detected: bool = False
        self.detected_glas_frames = []
        self.cycles_counter: int = 0
        self.ref_pos = (0, 0, 0, 0)  # x1, y1, x2, y2

        self.central_layout = QHBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        self.groupbox_glas_extraction = QGroupBox()
        self.groupbox_glas_extraction.setObjectName(u"groupbox_glas_extraction")
        self.groupbox_glas_extraction.setTitle(u"Glas Detection")
        self.groupbox_glas_extraction_layout = QHBoxLayout(self.groupbox_glas_extraction)
        self.groupbox_glas_extraction_layout.setObjectName(u"groupbox_glas_extraction_layout")

        self.glas_extraction_image_widget = ImageWidget()
        self.glas_extraction_image_widget.setObjectName(u"glas_extraction_image_widget")
        self.groupbox_glas_extraction_layout.addWidget(self.glas_extraction_image_widget)
        self.central_layout.addWidget(self.groupbox_glas_extraction)

    def detect_glas(self, frame: np.ndarray):

        ret = bv.glas_detection(frame.copy())

        # No glas detected on this frame
        if ret is None:
            self.cycles_counter = 0
            return

        frame, x, y, w, h = ret

        # Currently, there is no detected BoundingBox available
        if self.ref_pos == (0, 0, 0, 0):
            self.ref_pos = (x, y, x + w, y + h)
            return

        if abs(self.ref_pos[0] - x) > 10 or abs(self.ref_pos[1] - y) > 10 or abs(self.ref_pos[2] - w) > 30 or \
                abs(self.ref_pos[3] - h) > 30:
            self.ref_pos = (x, y, x+w, y+h)
            self.cycles_counter = 0
        else:
            self.cycles_counter += 1

        # Draw the found bounding-box
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        if self.cycles_counter >= 30:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            self.glas_detected = True
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 3)

        print(self.cycles_counter)

        return frame

    def update_image(self, frame: np.ndarray):
        """
        Glas detection has finished, when the program detects the glas on 30 cycles on the same spot
        :param frame:
        :return:
        """

        self.__glas_detector.detect(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        x, y, x2, y2 = self.__glas_detector.estimated_glas()
        if self.__glas_detector.state():
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 3)
        elif x is not None:
            cv2.rectangle(frame, (x, y), (x2, y2), (255, 255, 0), 3)

        # frame = self.detect_glas(frame)

        self.glas_extraction_image_widget.update_image(frame)
