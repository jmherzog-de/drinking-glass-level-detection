import cv2
import operator
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QLabel, QVBoxLayout
from .image_widget import ImageWidget
import numpy as np


class ROITabWidget(QWidget):

    def __init__(self, roi_update_callback, default_p1: tuple = (0, 0), default_p2: tuple = (2048, 2048)):
        super().__init__()
        self.__roi_update_callback_fct = roi_update_callback
        self.__glas_p1 = (0, 0)
        self.__glas_p2 = (0, 0)
        self.__p1 = default_p1
        self.__p2 = default_p2
        self.glass_type = -1
        self.fill_level = -1
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

        # Info Controls
        self.info_groupbox = QGroupBox()
        self.info_groupbox.setObjectName(u"info_groupbox")
        self.info_groupbox.setTitle(u"Information")
        self.info_groupbox.setMaximumWidth(220)
        self.info_groupbox.setMaximumHeight(220)

        self.info_groupbox_layout = QVBoxLayout(self.info_groupbox)
        self.info_groupbox_layout.setObjectName(u"info_groupbox_layout")

        self.glas_type_label = QLabel()
        self.glas_type_label.setObjectName(u"glas_type_label")
        self.glas_type_label.setText(u"Glass: -")

        self.fill_level_label = QLabel()
        self.fill_level_label.setObjectName(u"fill_level_label")
        self.fill_level_label.setText(u"Fill Level: - mm")

        self.info_groupbox_layout.addWidget(self.glas_type_label)
        self.info_groupbox_layout.addWidget(self.fill_level_label)

        # ROI Image Widget
        self.roi_image_groupbox = QGroupBox()
        self.roi_image_groupbox.setObjectName(u"roi_image_groupbox")
        self.roi_image_groupbox_layout = QHBoxLayout(self.roi_image_groupbox)
        self.roi_image_groupbox_layout.setObjectName(u"roi_image_groupbox_layout")

        self.roi_image_widget = ImageWidget()
        self.roi_image_widget.setObjectName(u"roi_image_widget")
        self.roi_image_groupbox_layout.addWidget(self.roi_image_widget)

        self.central_layout.addWidget(self.groupbox_controls)
        self.central_layout.addWidget(self.info_groupbox)
        self.central_layout.addWidget(self.roi_image_groupbox)

    @Slot()
    def __select_roi_clicked(self):
        self.__p1 = (int(self.roi_textbox_x1.text()), int(self.roi_textbox_y1.text()))
        self.__p2 = (int(self.roi_textbox_x2.text()), int(self.roi_textbox_y2.text()))
        self.__roi_update_callback_fct()

    def update_roi(self, p1: tuple, p2: tuple):
        self.__p1 = p1
        self.__p2 = p2
        self.roi_textbox_x1.setText(str(p1[0]))
        self.roi_textbox_y1.setText(str(p1[1]))
        self.roi_textbox_x2.setText(str(p2[0]))
        self.roi_textbox_y2.setText(str(p2[1]))

    def update_glas_rect(self, p1: tuple, p2: tuple):

        # Transform detected glas points into original frame size
        self.__glas_p1 = tuple(map(operator.add, self.__p1, p1))
        self.__glas_p2 = tuple(map(operator.add, self.__p1, p2))

    def update_image(self, frame: np.ndarray):

        if self.glass_type == 0:
            self.glas_type_label.setText(u"Glass: Small")
        elif self.glass_type == 1:
            self.glas_type_label.setText(u"Glass: Large")

        self.roi_image = frame[self.__p1[1]:self.__p2[1], self.__p1[0]:self.__p2[0]].copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        if not self.__glas_p2 == (0, 0):
            frame = cv2.rectangle(frame, self.__glas_p1, self.__glas_p2, color=(0, 255, 0), thickness=2)

        frame = cv2.rectangle(frame, self.__p1, self.__p2, color=(255, 0, 0), thickness=3)

        self.roi_image_widget.update_image(frame)
