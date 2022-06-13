from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox
from .image_widget import ImageWidget
import bv_algorithms as bv
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

    def update_image(self, diff_frame: np.ndarray):
        new_frame = bv.level_detection(diff_frame.copy())
        self.contours_image_widget.update_image(new_frame)
