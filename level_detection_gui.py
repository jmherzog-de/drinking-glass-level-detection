import sys
import cv2
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout)
from qt_widgets import NavigationWidget, RefImageTabWidget, ROITabWidget, LevelDetectionTabWidget, GlasDetectionTabWidget
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

        self.frame_counter = 0
        self.mode = "VIDEO"   # 'CAMERA' | 'VIDEO'
        self.orig_image = np.zeros(shape=(2048, 2048), dtype='uint8')

        self.bv_scale = AutoscaleImage()
        self.bv_scale.create_lookup_table(t_min=1000, t_max=20000)

        self.video_player = VideoPlayer()
        self.video_player.update_frame.connect(self.update_frame)

        self.pco_stream = QtVideoCapture()
        self.pco_stream.update_frame.connect(self.update_frame)

        self.setWindowTitle("Level Detection with PCO Camera")
        # self.setGeometry(0, 0, 800, 800)
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

        self.roi_widget = ROITabWidget(roi_update_callback=self.roi_selected_callback,
                                       default_p1=(500, 250), default_p2=(1300, 1850))
        self.roi_widget.setObjectName(u"roi_widget")
        self.roi_tab_page_layout.addWidget(self.roi_widget)

        #
        # MainTab: Glas Detection
        #
        self.glas_detection_tab_page = QWidget()
        self.glas_detection_tab_page.setObjectName(u"glas_detection_tab_page")
        self.glas_detection_tab_page_layout = QHBoxLayout(self.glas_detection_tab_page)
        self.glas_detection_tab_page_layout.setObjectName(u"glas_detection_tab_page_layout")

        self.glas_detection_tab_widget = GlasDetectionTabWidget()
        self.glas_detection_tab_widget.setObjectName(u"glas_detection_tab_widget")
        self.glas_detection_tab_page_layout.addWidget(self.glas_detection_tab_widget)

        #
        # MainTab: Apply Reference Image
        #
        self.refimg_tab_page = QWidget()
        self.refimg_tab_page.setObjectName(u"refimg_tab_page")
        self.refimg_tab_page_layout = QHBoxLayout(self.refimg_tab_page)
        self.refimg_tab_page_layout.setObjectName(u"refimg_tab_page_layout")

        self.refimg_tab_widget = RefImageTabWidget()
        self.refimg_tab_widget.setObjectName(u"refimg_tab_widget")
        self.refimg_tab_page_layout.addWidget(self.refimg_tab_widget)

        #
        # MainTab: Filling
        #
        self.filling_tab_page = QWidget()
        self.filling_tab_page.setObjectName(u"filling_tab_page")
        self.filling_tab_page_layout = QVBoxLayout(self.filling_tab_page)
        self.filling_tab_page_layout.setObjectName(u"filling_tab_page_layout")

        self.level_detection_tab_widget = LevelDetectionTabWidget()
        self.level_detection_tab_widget.setObjectName(u"level_detection_tab_widget")
        self.filling_tab_page_layout.addWidget(self.level_detection_tab_widget)

        self.main_tab.addTab(self.roi_tab_page, "1. Select ROI")
        self.main_tab.addTab(self.glas_detection_tab_page, "2. Glas Detection")
        self.main_tab.addTab(self.refimg_tab_page, "3. Apply Reference Image")
        self.main_tab.addTab(self.filling_tab_page, "4. Level Detection")

        self.setCentralWidget(self.central_widget)

    @Slot()
    def roi_selected_callback(self):
        pass    # TODO: Implement update frame on paused or ended video

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
        self.mode = 'CAMERA'

        self.pco_stream.capture_enabled = True
        self.pco_stream.start()

    @Slot()
    def stop_stream_clicked(self):
        self.pco_stream.capture_enabled = False

    @Slot()
    def save_reference_image_clicked(self):
        pass

    def update_frame(self, frame: np.ndarray):
        # Preprocess image before update on GUI
        if self.mode == "VIDEO":
            self.orig_image = frame    # Input image is a 8 bit image
        else:
            image = self.bv_scale.autoscale(frame)    # Input image is a 16 bit image
            self.orig_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # Display detected glas region
        if self.glas_detection_tab_widget.glas_detector.state():
            glas_stencil = self.glas_detection_tab_widget.glas_detector.get_glas_mask()
            self.level_detection_tab_widget.level_detector.set_glass_mask(glas_stencil)
            x1, y1, x2, y2 = self.glas_detection_tab_widget.glas_detector.estimated_glas()
            self.roi_widget.update_glas_rect((x1, y1), (x2, y2))

        self.roi_widget.update_image(self.orig_image)
        self.glas_detection_tab_widget.update_image(self.roi_widget.roi_image)

        tab_index = self.main_tab.currentIndex()

        if tab_index == 2 or tab_index == 3:
            if self.glas_detection_tab_widget.glas_detector.state():
                f = self.glas_detection_tab_widget.glas_detector.get_glas_frame()
                self.refimg_tab_widget.update_image(f.copy())
        if tab_index == 3 and self.frame_counter == 2:
            self.level_detection_tab_widget.update_image(self.refimg_tab_widget.diff_image)

        self.frame_counter = 0 if self.frame_counter == 2 else self.frame_counter + 1


if __name__ == '__main__':
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
