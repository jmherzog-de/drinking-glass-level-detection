import sys
from PySide6.QtCore import Qt, Slot, QRect
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QGroupBox, QHBoxLayout, QMenu, QMenuBar)
from PySide6.QtGui import QAction
from qt_widgets import ROIWidget, ImageWidget, NavigationWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.mode = "VIDEO"   # 'CAMERA' | 'VIDEO'

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

        self.main_tab = QTabWidget(self.central_widget)
        self.main_tab.setObjectName(u"main_tab")

        #
        # Qt Menu Bar (TOP)
        #

        self.main_nav_widget = NavigationWidget(self.open_video_file_clicked, self.open_camera_stream_clicked)
        self.main_nav_widget.setObjectName(u"main_nav_widget")
        self.central_widget_layout.addWidget(self.main_nav_widget)

        # MainTab: ROI Selection
        self.roi_tab_page = QWidget()
        self.roi_tab_page.setObjectName(u"roi_tab")
        self.roi_tab_page_layout = QHBoxLayout(self.roi_tab_page)
        self.roi_tab_page_layout.setObjectName(u"roi_tab_page_layout")

        self.roi_widget = ROIWidget(self.roi_selected_callback)
        self.roi_widget.setObjectName(u"roi_widget")
        self.roi_widget.setMaximumWidth(400)
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

        self.roi_original_image = ImageWidget()
        self.roi_original_image.setObjectName(u"roi_original_image")
        self.roi_images_layout.addWidget(self.roi_original_image)

        # MainTab: Apply Reference Image
        self.refimg_tab_page = QWidget()
        self.refimg_tab_page.setObjectName(u"refimg_tab_page")
        self.refimg_tab_page_layout = QVBoxLayout(self.main_tab)
        self.refimg_tab_page_layout.setObjectName(u"refimg_tab_page_layout")

        # MainTab: Filling
        self.filling_tab_page = QWidget()
        self.filling_tab_page.setObjectName(u"filling_tab_page")
        self.filling_tab_page_layout = QVBoxLayout(self.main_tab)
        self.filling_tab_page_layout.setObjectName(u"filling_tab_page_layout")

        self.main_tab.addTab(self.roi_tab_page, "1. Select ROI")
        self.main_tab.addTab(self.refimg_tab_page, "2. Apply Reference Image")
        self.main_tab.addTab(self.filling_tab_page, "3. Level Detection")

        self.central_widget_layout.addWidget(self.main_tab)
        self.setCentralWidget(self.central_widget)

    @Slot()
    def roi_selected_callback(self):
        pass

    @Slot()
    def open_camera_stream_clicked(self):
        self.main_nav_widget.enable_stream_controls()
        self.main_nav_widget.disable_video_controls()

    @Slot()
    def open_video_file_clicked(self):
        self.main_nav_widget.enable_video_controls()
        self.main_nav_widget.disable_stream_controls()


if __name__ == '__main__':
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
