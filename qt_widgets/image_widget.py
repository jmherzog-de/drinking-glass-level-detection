from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import numpy as np


class ImageWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.central_layout = QVBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        self.__image = QLabel(self)
        self.__image.setObjectName("image")
        self.__image.setMinimumSize(QSize(512, 512))
        self.__image.setMaximumSize(QSize(1024, 1024))
        self.__image.setStyleSheet(u"background-color: rgb(0, 0, 0);")
        self.__image.setAlignment(Qt.AlignCenter)
        self.central_layout.addWidget(self.__image)

    def __convert_cv_qt(self, image: np.ndarray):
        h, w, c = None, None, None
        if len(image.shape) == 2:
            h, w = image.shape
        elif len(image.shape) == 3:
            h, w, c = image.shape
        else:
            raise Exception("Invalid frame input.\n")

        if str(image.dtype) == "uint16":
            q_image = QImage(image.data, w, h, w * 2, QImage.Format_Grayscale16)
        else:
            if c is None:
                q_image = QImage(image.data, w, h, w, QImage.Format_Grayscale8)
            else:
                q_image = QImage(image.data, w, h, w * 3, QImage.Format_RGB888)

        return q_image.scaled(self.__image.width(), self.__image.height(), Qt.KeepAspectRatio)

    def update_image(self, image: np.ndarray):

        if not isinstance(image, np.ndarray):
            return

        q_pixmap = self.__convert_cv_qt(image)
        self.__image.setPixmap(QPixmap.fromImage(q_pixmap))
