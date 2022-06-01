import cv2
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QVBoxLayout
from .image_widget import ImageWidget
import numpy as np


class GlasDetectionTabWidget(QWidget):

    def __init__(self):
        super().__init__()

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

    def update_image(self, frame: np.ndarray):
        frame = cv2.blur(frame, (3, 3), cv2.BORDER_DEFAULT)
        frame = cv2.Canny(frame, 40, 150)
        frame = cv2.dilate(frame, np.ones((5, 5), np.uint8), 8)
        self.glas_extraction_image_widget.update_image(frame)
