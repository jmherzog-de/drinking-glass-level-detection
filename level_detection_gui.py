import sys

import cv2
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QGroupBox,
                               QHBoxLayout)
from qt_widgets import ROIWidget, ImageWidget, NavigationWidget
from cv_videoplayer import VideoPlayer
from pco_capture import QtVideoCapture
from bv_algorithms import AutoscaleImage
import numpy as np


class MainWindow(QMainWindow):
    """
    MainWindow Qt GUI

    :param QMainWindow: Qt parent class
    :type QMainWindow: Any
    """

    def __init__(self):
        """
        Default class constructor for MainWindow.
        Initialize all UI widgets.
        """
        super().__init__()

        self.mode = "VIDEO"   # 'CAMERA' | 'VIDEO'
        self.roi_p1 = (0, 0)
        self.roi_p2 = (2048, 2048)

        self.bv_scale = AutoscaleImage()
        self.bv_scale.create_lookup_table(t_min=1000, t_max=20000)

        self.video_player = VideoPlayer()
        self.video_player.update_frame.connect(self.update_frame)

        self.pco_stream = QtVideoCapture()
        self.pco_stream.update_frame.connect(self.update_frame)

        self.setWindowTitle("Level Detection with PCO Camera")
        self.setGeometry(0, 0, 800, 800)
        self.showMaximized()

        #
        # Base Widget
        #

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName(u"central_widget")

        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.central_widget_layout.setObjectName(u"central_widget_layout")

        #
        # Qt Menu Bar (TOP)
        #

        self.main_nav_widget = NavigationWidget(open_video_file_callback=self.open_video_file_clicked,
                                                open_pco_stream_callback=self.open_camera_stream_clicked,
                                                play_video_callback=self.play_video_clicked,
                                                pause_video_callback=self.pause_video_clicked,
                                                stop_video_callback=self.stop_video_clicked,
                                                start_stream_callback=self.start_stream_clicked,
                                                stop_stream_callback=self.stop_stream_clicked)
        self.main_nav_widget.setObjectName(u"main_nav_widget")
        self.central_widget_layout.addWidget(self.main_nav_widget)

        self.main_tab = QTabWidget(self.central_widget)
        self.main_tab.setObjectName(u"main_tab")
        self.central_widget_layout.addWidget(self.main_tab)

        # MainTab: ROI Selection
        self.roi_tab_page = QWidget()
        self.roi_tab_page.setObjectName(u"roi_tab")
        self.roi_tab_page_layout = QHBoxLayout(self.roi_tab_page)
        self.roi_tab_page_layout.setObjectName(u"roi_tab_page_layout")

        self.roi_widget = ROIWidget(self.roi_selected_callback)
        self.roi_widget.setObjectName(u"roi_widget")
        self.roi_widget.setMaximumWidth(450)
        self.roi_widget.setMaximumHeight(220)
        self.roi_tab_page_layout.addWidget(self.roi_widget, Qt.AlignBottom)

        self.roi_images_groupbox = QGroupBox()
        self.roi_images_groupbox.setObjectName(u"roi_images_groupbox")
        self.roi_images_layout = QHBoxLayout(self.roi_images_groupbox)
        self.roi_images_layout.setObjectName(u"roi_images_layout")
        self.roi_tab_page_layout.addWidget(self.roi_images_groupbox)

        self.roi_image = ImageWidget()
        self.roi_image.setObjectName(u"roi_image")
        self.roi_images_layout.addWidget(self.roi_image)

        # MainTab: Apply Reference Image
        self.refimg_tab_page = QWidget()
        self.refimg_tab_page.setObjectName(u"refimg_tab_page")
        self.refimg_tab_page_layout = QVBoxLayout(self.refimg_tab_page)
        self.refimg_tab_page_layout.setObjectName(u"refimg_tab_page_layout")

        # MainTab: Filling
        self.filling_tab_page = QWidget()
        self.filling_tab_page.setObjectName(u"filling_tab_page")
        self.filling_tab_page_layout = QVBoxLayout(self.filling_tab_page)
        self.filling_tab_page_layout.setObjectName(u"filling_tab_page_layout")

        self.main_tab.addTab(self.roi_tab_page, "1. Select ROI")
        self.main_tab.addTab(self.refimg_tab_page, "2. Apply Reference Image")
        self.main_tab.addTab(self.filling_tab_page, "3. Level Detection")

        self.setCentralWidget(self.central_widget)

    @Slot()
    def roi_selected_callback(self):
        self.roi_p1 = ( int(self.roi_widget.roi_text_edit_x1.text()), int(self.roi_widget.roi_text_edit_y1.text()))
        self.roi_p2 = ( int(self.roi_widget.roi_text_edit_x2.text()), int(self.roi_widget.roi_text_edit_y2.text()))

    @Slot()
    def open_camera_stream_clicked(self):
        self.main_nav_widget.enable_stream_controls()
        self.main_nav_widget.disable_video_controls()

    @Slot()
    def open_video_file_clicked(self):

        # Open FileDialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video", filter="Video File (*.mp4)")
        if file_name:
            self.video_player.video_file_path = file_name
        self.main_nav_widget.enable_video_controls()
        self.main_nav_widget.disable_stream_controls()

    @Slot()
    def play_video_clicked(self):
        self.video_player.start()

    @Slot()
    def pause_video_clicked(self):
        pass

    @Slot()
    def stop_video_clicked(self):
        self.video_player.play = False

    @Slot()
    def start_stream_clicked(self):
        pass

    @Slot()
    def stop_stream_clicked(self):
        pass

    def update_roi_image(self, image: np.ndarray):
        cv2.rectangle(image, self.roi_p1, self.roi_p2, color=(255, 255, 255), thickness=3)
        self.roi_image.update_image(image)

    def update_frame(self, frame: np.ndarray):
        # Preprocess image before update on GUI
        if self.mode == "VIDEO":
            image = frame    # Input image is a 8 bit image
        else:
            image = self.bv_scale.autoscale(frame)    # Input image is a 16 bit image
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        tab_index = self.main_tab.currentIndex()

        if tab_index == 0:
            self.update_roi_image(image)


if __name__ == '__main__':
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
