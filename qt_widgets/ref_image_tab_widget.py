from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGroupBox, QSlider, QVBoxLayout, QLabel
from .image_widget import ImageWidget
import bv_algorithms as bv
import numpy as np


class RefImageTabWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.__diff_image_set = False
        self.__diff_image_builder = bv.DifferenceImageBuilder()

        self.active_frame = np.ndarray(shape=(2048, 2048), dtype='uint8')
        self.ref_image = np.ndarray(shape=(2048, 2048), dtype='uint8')
        self.diff_image = np.ndarray(shape=(2048, 2048), dtype='uint8')

        self.central_layout = QHBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        # Reference Image Params
        self.groupbox_reference_image = QGroupBox()
        self.groupbox_reference_image.setObjectName(u"groupbox_reference_image")
        self.groupbox_reference_image.setTitle(u"Reference Image")
        self.groupbox_reference_image_layout = QVBoxLayout(self.groupbox_reference_image)
        self.groupbox_reference_image_layout.setObjectName(u"groupbox_reference_image_layout")

        self.select_ref_image_button = QPushButton()
        self.select_ref_image_button.setObjectName(u"select_ref_image_button")
        self.select_ref_image_button.setText(u"Select frame as Reference Image")
        self.select_ref_image_button.clicked.connect(self.__save_ref_image)
        self.groupbox_reference_image_layout.addWidget(self.select_ref_image_button)

        self.reference_image = ImageWidget()
        self.reference_image.setObjectName(u"reference_image")
        self.groupbox_reference_image_layout.addWidget(self.reference_image)

        self.live_image = ImageWidget()
        self.live_image.setObjectName(u"live_image")
        self.groupbox_reference_image_layout.addWidget(self.live_image)

        # Difference Image Params
        self.groupbox_difference_image = QGroupBox()
        self.groupbox_difference_image.setObjectName(u"groupbox_difference_image")
        self.groupbox_difference_image.setTitle(u"Difference Image")
        self.groupbox_difference_image_layout = QVBoxLayout(self.groupbox_difference_image)
        self.groupbox_difference_image_layout.setObjectName(u"groupbox_difference_image_layout")

        self.distance_slider = QSlider(Qt.Horizontal)
        self.distance_slider.setObjectName(u"distance_slider")
        self.distance_slider.setMinimum(10)
        self.distance_slider.setMaximum(200)
        self.distance_slider.setValue(100)
        self.distance_slider.valueChanged.connect(self.__slider_value_changed)
        self.groupbox_difference_image_layout.addWidget(self.distance_slider)

        self.current_distance_label = QLabel()
        self.current_distance_label.setObjectName(u"current_distance_label")
        self.current_distance_label.setText(f"{self.__diff_image_builder.distance}")
        self.current_distance_label.setMaximumHeight(20)
        self.groupbox_difference_image_layout.addWidget(self.current_distance_label)

        self.difference_image = ImageWidget()
        self.difference_image.setObjectName(u"difference_image")
        self.groupbox_difference_image_layout.addWidget(self.difference_image)

        self.central_layout.addWidget(self.groupbox_reference_image)
        self.central_layout.addWidget(self.groupbox_difference_image)

    def __slider_value_changed(self, value: int):
        self.__diff_image_builder.distance = value
        self.current_distance_label.setText(f"{value}")

    def __save_ref_image(self):
        self.__diff_image_builder.set_reference_image(self.active_frame.copy())
        self.reference_image.update_image(self.active_frame.copy())
        self.__diff_image_set = True

    def ref_image_state(self):
        return self.__diff_image_set

    def set_ref_image(self):
        self.__save_ref_image()

    def update_image(self, frame: np.ndarray):
        self.active_frame = frame.copy()
        self.live_image.update_image(frame)

        if self.__diff_image_set:
            self.diff_image = self.__diff_image_builder.build(self.active_frame)
            self.difference_image.update_image(self.diff_image)
