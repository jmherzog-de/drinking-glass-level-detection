import cv2
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QVBoxLayout
from .image_widget import ImageWidget
import numpy as np


class LevelDetectionTabWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.central_layout = QHBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")
