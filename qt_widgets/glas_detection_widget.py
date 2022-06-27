import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox

import bv_algorithms as bv
from .image_widget import ImageWidget


class GlassDetectionTabWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.glass_detector = bv.GlassDetection()

        self.glass_detected: bool = False
        self.detected_glass_frames = []
        self.cycles_counter: int = 0
        self.ref_pos = (0, 0, 0, 0)  # x1, y1, x2, y2

        self.central_layout = QHBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        self.groupbox_glass_extraction = QGroupBox()
        self.groupbox_glass_extraction.setObjectName(u"groupbox_glass_extraction")
        self.groupbox_glass_extraction.setTitle(u"Glas Detection")
        self.groupbox_glass_extraction_layout = QHBoxLayout(self.groupbox_glass_extraction)
        self.groupbox_glass_extraction_layout.setObjectName(u"groupbox_glass_extraction_layout")

        self.glass_extraction_image_widget = ImageWidget()
        self.glass_extraction_image_widget.setObjectName(u"glass_extraction_image_widget")
        self.groupbox_glass_extraction_layout.addWidget(self.glass_extraction_image_widget)

        self.glass_stencil_widget = ImageWidget()
        self.glass_stencil_widget.setObjectName(u"glass_stencil_image_widget")
        self.groupbox_glass_extraction_layout.addWidget(self.glass_stencil_widget)

        self.central_layout.addWidget(self.groupbox_glass_extraction)

    def update_image(self, frame: np.ndarray):
        """
        Glass detection has finished, when the program detects the glass on 30 cycles on the same spot
        :param frame:
        :return:
        """

        frame = self.glass_detector.detect(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        x, y, x2, y2 = self.glass_detector.estimated_glass()
        if self.glass_detector.state():
            self.glass_stencil_widget.update_image(self.glass_detector.get_glass_stencil())
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 3)
        elif x is not None:
            cv2.rectangle(frame, (x, y), (x2, y2), (255, 255, 0), 3)

        self.glass_extraction_image_widget.update_image(frame)
