import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox

import bv_algorithms as bv
from .image_widget import ImageWidget


class GlasDetectionTabWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.glas_detector = bv.GlassDetection()

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

        self.glas_stencil_widget = ImageWidget()
        self.glas_stencil_widget.setObjectName(u"glas_stencil_image_widget")
        self.groupbox_glas_extraction_layout.addWidget(self.glas_stencil_widget)

        self.central_layout.addWidget(self.groupbox_glas_extraction)

    def update_image(self, frame: np.ndarray):
        """
        Glas detection has finished, when the program detects the glas on 30 cycles on the same spot
        :param frame:
        :return:
        """

        frame = self.glas_detector.detect(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        x, y, x2, y2 = self.glas_detector.estimated_glas()
        if self.glas_detector.state():
            self.glas_stencil_widget.update_image(self.glas_detector.get_glas_stencil())
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 3)
        elif x is not None:
            cv2.rectangle(frame, (x, y), (x2, y2), (255, 255, 0), 3)

        self.glas_extraction_image_widget.update_image(frame)
