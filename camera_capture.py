import cv2
import sys
import numpy as np
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox, QHBoxLayout)
from pco_capture import QtVideoCapture
from qt_widgets import ImageWidget, HistogramWidget, CameraControlsWidget, VideoControlsWidget
from bv_algorithms import AutoscaleImage
from cv_videoplayer import VideoPlayer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.__mode = "VIDEO"   # 'CAMERA' | 'VIDEO'
        self.__record_video = False
        self.__video = None

        self.__autosale = AutoscaleImage()
        self.__autosale.create_lookup_table(t_min=1000, t_max=20000)

        self.__reference_image = np.zeros(shape=(2048, 2048), dtype='uint8')
        self.__difference_image = self.__reference_image.copy()

        self.__capture = QtVideoCapture()
        self.__capture.finished.connect(self.stop_capture_clicked_event)
        self.__capture.update_frame.connect(self.update_image)

        self.__video_player = VideoPlayer()
        self.__video_player.finished.connect(self.stop_video_clicked_event)
        self.__video_player.update_frame.connect(self.update_image)

        self.__hist_update_counter = -1
        self.__frame_counter = 0
        self.__image_counter = 0

        self.setWindowTitle("Capture PCO Images")
        self.setGeometry(0, 0, 800, 800)
        self.showMaximized()

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName(u"central_widget")

        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setObjectName(u"central_layout")

        # Add Video Control Widget to GUI
        self.video_controls = VideoControlsWidget(self.start_video_capture_clicked_event,
                                                  self.stop_video_capture_clicked_event,
                                                  self.start_video_clicked_event,
                                                  self.stop_video_clicked_event)
        self.video_controls.setObjectName(u"video_controls")
        self.central_layout.addWidget(self.video_controls)

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

        # TabPage: Difference Image
        self.difference_image_tab_page = QWidget()
        self.difference_image_tab_page.setObjectName(u"difference_image_tab_page")
        self.main_tab.addTab(self.difference_image_tab_page, "Difference Image")
        self.difference_image_tab_page_layout = QHBoxLayout(self.difference_image_tab_page)
        self.difference_image_tab_page_layout.setObjectName(u"difference_image_tab_page_layout")

        self.difference_image_filters_tab = QTabWidget()
        self.difference_image_filters_tab.setObjectName(u"difference_image_filters_tab")
        self.difference_image_tab_page_layout.addWidget(self.difference_image_filters_tab)

        self.reference_image_widget = ImageWidget()
        self.reference_image_widget.setObjectName(u"reference_image_widget")
        self.difference_image_tab_page_layout.addWidget(self.reference_image_widget)

        self.diffimg_live_widget = ImageWidget()
        self.diffimg_live_widget.setObjectName(u"diffimg_live_widget")
        self.difference_image_tab_page_layout.addWidget(self.diffimg_live_widget)

        # TabPage: Difference Image -> Display Difference Image
        self.diffimg_tab_page = QWidget()
        self.diffimg_tab_page.setObjectName(u"diffimg_tab_page")
        self.difference_image_filters_tab.addTab(self.diffimg_tab_page, "Difference Image")
        self.diffimg_tab_page_layout = QHBoxLayout(self.diffimg_tab_page)
        self.diffimg_tab_page_layout.setObjectName(u"diffimg_tab_page_layout")

        self.difference_image_widget = ImageWidget()
        self.difference_image_widget.setObjectName(u"difference_image_widget")
        self.diffimg_tab_page_layout.addWidget(self.difference_image_widget)

        # TabPage: Difference Image -> Sobel Y
        self.diffimg_sobel_y_tab_page = QWidget()
        self.diffimg_sobel_y_tab_page.setObjectName(u"diffimg_sobel_y_tab_page")
        self.difference_image_filters_tab.addTab(self.diffimg_sobel_y_tab_page, "Sobel-Y")
        self.diffimg_sobel_y_tab_page_layout = QHBoxLayout(self.diffimg_sobel_y_tab_page)
        self.diffimg_sobel_y_tab_page_layout.setObjectName(u"diffimg_sobel_y_tab_page_layout")

        self.difference_image_sobel_y_widget = ImageWidget()
        self.difference_image_sobel_y_widget.setObjectName(u"difference_image_sobel_y_widget")
        self.diffimg_sobel_y_tab_page_layout.addWidget(self.difference_image_sobel_y_widget)

        # TabPage: Difference Image -> Contours
        self.diffimg_contours_tab_page = QWidget()
        self.diffimg_contours_tab_page.setObjectName(u"diffimg_contours_tab_page")
        self.difference_image_filters_tab.addTab(self.diffimg_contours_tab_page, "Contours")
        self.diffimg_contours_tab_page_layout = QHBoxLayout(self.diffimg_contours_tab_page)
        self.diffimg_contours_tab_page_layout.setObjectName(u"diffimg_contours_tab_page_layout")

        self.diffimg_contours_widget = ImageWidget()
        self.diffimg_contours_widget.setObjectName(u"diffimg_contours_widget")
        self.diffimg_contours_tab_page_layout.addWidget(self.diffimg_contours_widget)

        self.setCentralWidget(self.central_widget)

    @Slot()
    def start_video_capture_clicked_event(self):
        self.__record_video = True
        self.__video = cv2.VideoWriter(self.video_controls.getVideoPath(), cv2.VideoWriter_fourcc(*'X264'), 20, (2048, 2048))
        self.video_controls.disable_capture_button()
        self.start_capture_clicked_event()

    @Slot()
    def stop_video_capture_clicked_event(self):
        self.__record_video = False
        self.__video.release()
        self.video_controls.enable_capture_button()
        self.stop_capture_clicked_event()

    @Slot()
    def start_capture_clicked_event(self):
        try:
            self.__mode = 'CAMERA'
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

    @Slot()
    def start_video_clicked_event(self):
        try:
            self.__mode = 'VIDEO'
            self.__video_player.video_file_path = self.video_controls.getVideoPath()
            self.__video_player.start()
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
    def stop_video_clicked_event(self):
        pass

    def update_original_16bit_images(self, image: np.ndarray, scaled_image: np.ndarray):
        self.live_image.update_image(image)
        self.live_image.update_image(scaled_image)

    def update_original_8bit_image(self, image8bit: np.ndarray):
        self.corrected_image.update_image(image8bit)

    def update_histograms_16bit(self, image16bit: np.ndarray, scaled16bit: np.ndarray):
        if self.__hist_update_counter == 20:
            self.histogram_widget.update_histogram(name="Original Image", image=image16bit)
            self.histogram_widget.update_histogram(name="Autoscaled Image", image=scaled16bit)
        else:
            self.__hist_update_counter += 1

    def update_histograms_8bit(self, image8bit: np.ndarray):
        if self.__hist_update_counter == 20:
            self.histogram_corrected_widget.update_histogram(name="Original Image", image=image8bit)
        else:
            self.__hist_update_counter += 1

    def update_difference_image(self, image8bit: np.ndarray):
        if self.__frame_counter == 2:
            difference_image = np.where(abs(image8bit.astype('float64') - self.__reference_image) > 80, 255, 0)
            gray_y = cv2.Sobel(difference_image.astype('uint8'),
                               cv2.CV_8U, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
            contours, hierarchy = cv2.findContours(gray_y, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours_image = np.zeros(shape=(2048, 2048), dtype="uint8")
            contours_copy = []
            for cnt in contours:
                if cv2.contourArea(cnt) > 50:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(contours_image, (x, y), (x+w, y+h), (255, 0, 0), 3)
                    contours_copy.append(cnt)

            cv2.drawContours(contours_image, contours_copy, -1, (255, 255, 255), 4)
            self.__image_counter += 1
            self.reference_image_widget.update_image(self.__reference_image.astype('uint8'))
            self.diffimg_contours_widget.update_image(contours_image)
            self.difference_image_widget.update_image(difference_image.astype('uint8'))
            self.difference_image_sobel_y_widget.update_image(gray_y)
            self.diffimg_live_widget.update_image(image8bit)
            self.__frame_counter = 0
        else:
            self.__frame_counter += 1

    def update_image(self, image: np.ndarray):

        tab_index = self.main_tab.currentIndex()

        if not self.__mode == "VIDEO":
            scaled_image = self.__autosale.autoscale(image)
            image_8bit = cv2.normalize(scaled_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            if self.__record_video:
                self.__video.write(image_8bit)
        else:
            image_8bit = image

        if self.__hist_update_counter == -1:
            self.histogram_widget.add_histogram(name="Original Image", image=image.copy())
            self.histogram_widget.add_histogram(name="Autoscaled Image", image=image.copy())
            self.histogram_corrected_widget.add_histogram(name="Original Image", image=image_8bit.copy())
            self.__reference_image = image_8bit.astype('float64')
            self.reference_image_widget.update_image(image_8bit.copy())
            self.__hist_update_counter += 1

        # Update Image 16 Bit
        if tab_index == 0 and self.__mode == "CAMERA":
            self.update_original_16bit_images(image, scaled_image)

        # Update Image 8 Bit
        elif tab_index == 1:
            self.update_original_8bit_image(image_8bit)

        # Update 16 Bit Histogram
        elif tab_index == 2 and self.__mode == "CAMERA":
            self.update_histograms_16bit(image.copy(), scaled_image.copy())

        # Update 8 Bit Histogram
        elif tab_index == 3:
            self.update_histograms_8bit(image_8bit.copy())

        # Update Difference Image
        elif tab_index == 4:
            self.update_difference_image(image_8bit.copy())


if __name__ == '__main__':
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
