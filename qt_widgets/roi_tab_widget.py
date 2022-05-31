import cv2
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit
from .image_widget import ImageWidget
import numpy as np


class ROITabWidget(QWidget):

    def __init__(self, roi_update_callback, default_p1: tuple = (0, 0), default_p2: tuple = (2048, 2048)):
        super().__init__()
        self.__roi_update_callback_fct = roi_update_callback
        self.__p1 = default_p1
        self.__p2 = default_p2
        self.roi_image = np.zeros(shape=(2048, 2048), dtype='uint8')
        self.setObjectName(u"roi_tab_widget")   # Set default object name

        self.central_layout = QHBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        # ROI Controls
        self.groupbox_controls = QGroupBox()
        self.groupbox_controls.setObjectName(u"groupbox_controls")
        self.groupbox_controls.setTitle(u"Select ROI Coordinates")
        self.groupbox_controls.setMaximumWidth(220)
        self.groupbox_controls.setMaximumHeight(220)

        self.roi_form_layout = QFormLayout(self.groupbox_controls)
        self.roi_form_layout.setObjectName(u"roi_form_layout")

        self.roi_textbox_x1 = QLineEdit()
        self.roi_textbox_x1.setObjectName(u"roi_textbox_x1")
        self.roi_textbox_x1.setText(f"{self.__p1[0]}")
        self.roi_form_layout.addRow("x_1:", self.roi_textbox_x1)

        self.roi_textbox_y1 = QLineEdit()
        self.roi_textbox_y1.setObjectName(u"roi_textbox_y1")
        self.roi_textbox_y1.setText(f"{self.__p1[1]}")
        self.roi_form_layout.addRow("y_1:", self.roi_textbox_y1)

        self.roi_textbox_x2 = QLineEdit()
        self.roi_textbox_x2.setObjectName(u"roi_textbox_x2")
        self.roi_textbox_x2.setText(f"{self.__p2[0]}")
        self.roi_form_layout.addRow("x_2:", self.roi_textbox_x2)

        self.roi_textbox_y2 = QLineEdit()
        self.roi_textbox_y2.setObjectName(u"roi_textbox_y2")
        self.roi_textbox_y2.setText(f"{self.__p2[1]}")
        self.roi_form_layout.addRow("y_2:", self.roi_textbox_y2)

        self.select_button = QPushButton()
        self.select_button.setObjectName(u"select_button")
        self.select_button.setText(u"Select ROI")
        self.select_button.clicked.connect(self.__select_roi_clicked)
        self.roi_form_layout.addWidget(self.select_button)

        # ROI Image Widget
        self.roi_image_groupbox = QGroupBox()
        self.roi_image_groupbox.setObjectName(u"roi_image_groupbox")
        self.roi_image_groupbox_layout = QHBoxLayout(self.roi_image_groupbox)
        self.roi_image_groupbox_layout.setObjectName(u"roi_image_groupbox_layout")

        self.roi_image_widget = ImageWidget()
        self.roi_image_widget.setObjectName(u"roi_image_widget")
        self.roi_image_groupbox_layout.addWidget(self.roi_image_widget)

        self.central_layout.addWidget(self.groupbox_controls)
        self.central_layout.addWidget(self.roi_image_groupbox)

    @Slot()
    def __select_roi_clicked(self):
        self.__p1 = (int(self.roi_textbox_x1.text()), int(self.roi_textbox_y1.text()))
        self.__p2 = (int(self.roi_textbox_x2.text()), int(self.roi_textbox_y2.text()))
        self.__roi_update_callback_fct()

    def update_image(self, frame: np.ndarray):
        self.roi_image = frame[self.__p1[1]:self.__p2[1], self.__p1[0]:self.__p2[0]].copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        frame = cv2.rectangle(frame, self.__p1, self.__p2, color=(255, 0, 0), thickness=3)
        self.roi_image_widget.update_image(frame)
