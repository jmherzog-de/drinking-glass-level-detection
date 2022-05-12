import cv2
import sys
import numpy as np
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox, QHBoxLayout)
from pco_capture import QtVideoCapture
from qt_widgets import ImageWidget, HistogramWidget, CameraControlsWidget
from bv_algorithms import AutoscaleImage, DifferenceImage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.__autosale = AutoscaleImage()
        self.__autosale.create_lookup_table(t_min=1000, t_max=20000)

        self.__capture = QtVideoCapture()
        self.__capture.finished.connect(self.stop_capture_clicked_event)
        self.__capture.update_frame.connect(self.update_image)

        self.__hist_update_counter = -1

        self.setWindowTitle("Capture PCO Images")
        self.setGeometry(0, 0, 800, 800)
        self.showMaximized()

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName(u"central_widget")

        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setObjectName(u"central_layout")

        # Add Camera Controls Widget to GUI
        self.controls = CameraControlsWidget(start_trig_event=self.start_capture_clicked_event,
                                             stop_trig_event=self.stop_capture_clicked_event)
        self.controls.setObjectName(u"camera_controls_widget")
        self.central_layout.addWidget(self.controls)

        # Add TabWidget to GUI
        self.main_tab = QTabWidget(self.central_widget)
        self.main_tab.setObjectName(u"main_tab")
        self.central_layout.addWidget(self.main_tab)

        # TabPage: Live Image (16-Bit)
        self.live_image_tab_page = QWidget()
        self.live_image_tab_page.setObjectName(u"live_image_tab_page")
        self.main_tab.addTab(self.live_image_tab_page, "Live Image (16 Bit)")
        self.live_image_tab_page_layout = QHBoxLayout(self.live_image_tab_page)
        self.live_image_tab_page_layout.setObjectName(u"live_image_tab_page_layout")

        # Original Image (16 bit)
        self.live_image = ImageWidget()
        self.live_image_tab_page_layout.addWidget(self.live_image)

        # Auto-scaled Image (16 bit)
        self.live_image_scaled = ImageWidget()
        self.live_image_tab_page_layout.addWidget(self.live_image_scaled)

        # TabPage: Corrected Image
        self.corrected_image_tab_page = QWidget()
        self.corrected_image_tab_page.setObjectName(u"corrected_image_tab_page")
        self.main_tab.addTab(self.corrected_image_tab_page, "Live Image (8 Bit)")
        self.corrected_image_tab_page_layout = QVBoxLayout(self.corrected_image_tab_page)
        self.corrected_image_tab_page_layout.setObjectName(u"corrected_image_tab_page_layout")

        # Corrected Image
        self.corrected_image = ImageWidget()
        self.corrected_image_tab_page_layout.addWidget(self.corrected_image)

        # TabPage: Histogram (16-Bit Original Image)
        self.histogram_tab_page = QWidget()
        self.histogram_tab_page.setObjectName(u"histogram_tab_page")
        self.main_tab.addTab(self.histogram_tab_page, "Histogram (16 bit)")
        self.histogram_tab_page_layout = QHBoxLayout(self.histogram_tab_page)
        self.histogram_tab_page_layout.setObjectName(u"histogram_tab_page_layout")

        self.histogram_widget = HistogramWidget()
        self.histogram_widget.setObjectName(u"histogram_widget")
        self.histogram_tab_page_layout.addWidget(self.histogram_widget)

        # TabPage: Histogram corrected image
        self.histogram_corrected_tab_page = QWidget()
        self.histogram_corrected_tab_page.setObjectName(u"histogram_corrected_tab_page")
        self.main_tab.addTab(self.histogram_corrected_tab_page, "Histogram (8 bit)")
        self.histogram_corrected_tab_page_layout = QVBoxLayout(self.histogram_corrected_tab_page)
        self.histogram_corrected_tab_page_layout.setObjectName(u"histogram_corrected_tab_page_layout")

        self.histogram_corrected_widget = HistogramWidget()
        self.histogram_corrected_widget.setObjectName(u"histogram_corrected_widget")
        self.histogram_corrected_tab_page_layout.addWidget(self.histogram_corrected_widget)

        self.setCentralWidget(self.central_widget)

    @Slot()
    def start_capture_clicked_event(self):

        try:
            self.controls.disable_start_button()
            self.__capture.capture_enabled = True
            self.__capture.save_image = self.controls.get_checked_state()
            self.__capture.start()
        except Exception as err:
            msg_box = QMessageBox(self)
            msg_box.setText(str(err))
            msg_box.setInformativeText("Please check the connection and close other processes which use the camera.")
            msg_box.setWindowTitle("PCO Camera Error")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.exec()

    @Slot()
    def stop_capture_clicked_event(self):
        self.controls.enable_start_button()
        self.__capture.capture_enabled = False

    def update_image(self, image: np.ndarray):

        tab_index = self.main_tab.currentIndex()
        scaled_image = self.__autosale.autoscale(image)
        image_8bit = cv2.normalize(scaled_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        if self.__hist_update_counter == -1:
            self.histogram_widget.add_histogram(name="Original Image", image=image.copy())
            self.histogram_widget.add_histogram(name="Autoscaled Image", image=image.copy())
            self.histogram_corrected_widget.add_histogram(name="Original Image", image=image_8bit.copy())
            self.__hist_update_counter += 1

        #
        # Update Image 16 Bit
        #
        if tab_index == 0:
            self.live_image.update_image(image)
            self.live_image_scaled.update_image(scaled_image)

        #
        # Update Image 8 Bit
        #
        elif tab_index == 1:
            self.corrected_image.update_image(image_8bit)

        #
        # Update 16 Bit Histogram
        #
        elif tab_index == 2:
            if self.__hist_update_counter == 20:
                self.histogram_widget.update_histogram(name="Original Image", image=image.copy())
                self.histogram_widget.update_histogram(name="Autoscaled Image", image=scaled_image.copy())
            else:
                self.__hist_update_counter += 1

        #
        # Update 8 Bit Histogram
        #
        elif tab_index == 3:
            if self.__hist_update_counter == 20:
                self.histogram_corrected_widget.update_histogram(name="Original Image", image=image_8bit)
            else:
                self.__hist_update_counter += 1


if __name__ == '__main__':
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
