from PySide6.QtWidgets import QWidget, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog


class VideoControlsWidget(QWidget):

    def __init__(self, capture_start_trig_event, capture_stop_trig_event, play_video_trig_event, stop_video_trig_event):
        super().__init__()

        self.__central_layout = QHBoxLayout(self)
        self.__central_layout.setObjectName(u"central_layout")

        self.__groupbox = QGroupBox(self)
        self.__groupbox.setObjectName(u"groupbox")
        self.__groupbox.setTitle(u"Play/Capture Video")
        self.__central_layout.addWidget(self.__groupbox)

        self.__groupbox_layout = QVBoxLayout(self.__groupbox)
        self.__groupbox_layout.setObjectName(u"groupbox_layout")

        self.__line1_layout = QHBoxLayout()
        self.__line1_layout.setObjectName(u"line1_layout")
        self.__groupbox_layout.addLayout(self.__line1_layout)

        self.__path_label = QLabel(self)
        self.__path_label.setObjectName(u"path_label")
        self.__path_label.setText(u"-")

        self.__select_path_button = QPushButton(self)
        self.__select_path_button.setObjectName(u"select_path_button")
        self.__select_path_button.setText("Video path")
        self.__select_path_button.setMaximumWidth(100)
        self.__select_path_button.clicked.connect(self.__select_path)

        self.__line1_layout.addWidget(self.__path_label)
        self.__line1_layout.addWidget(self.__select_path_button)

        self.__line2_layout = QHBoxLayout()
        self.__line2_layout.setObjectName(u"line2_layout")
        self.__groupbox_layout.addLayout(self.__line2_layout)

        self.__capture_button = QPushButton(self)
        self.__capture_button.setObjectName(u"capture_button")
        self.__capture_button.setText(u"CAPTURE")
        self.__capture_button.clicked.connect(capture_start_trig_event)

        self.__capture_stop_button = QPushButton(self)
        self.__capture_stop_button.setObjectName(u"capture_stop_button")
        self.__capture_stop_button.setText(u"STOP CAPTURE")
        self.__capture_stop_button.clicked.connect(capture_stop_trig_event)

        self.__line2_layout.addWidget(self.__capture_button)
        self.__line2_layout.addWidget(self.__capture_stop_button)

        self.__line3_layout = QHBoxLayout()
        self.__line3_layout.setObjectName(u"line3_layout")
        self.__groupbox_layout.addLayout(self.__line3_layout)

        self.__play_button = QPushButton(self)
        self.__play_button.setObjectName(u"play_button")
        self.__play_button.setText(u"PLAY VIDEO")
        self.__play_button.clicked.connect(play_video_trig_event)

        self.__stop_button = QPushButton(self)
        self.__stop_button.setObjectName(u"stop_button")
        self.__stop_button.setText(u"STOP VIDEO")
        self.__stop_button.clicked.connect(stop_video_trig_event)

        self.__line3_layout.addWidget(self.__play_button)
        self.__line3_layout.addWidget(self.__stop_button)

    def __select_path(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Open video")
        if file_name:
            self.__path_label.setText(str(file_name))

    def disable_capture_button(self):
        self.__capture_button.setEnabled(False)
        self.__capture_stop_button.setEnabled(True)

    def enable_capture_button(self):
        self.__capture_stop_button.setEnabled(False)
        self.__capture_button.setEnabled(True)

    def getVideoPath(self):
        return self.__path_label.text()
