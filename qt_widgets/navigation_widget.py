from PySide6.QtWidgets import QWidget, QGroupBox, QPushButton, QHBoxLayout, QCheckBox


class NavigationWidget(QWidget):

    def __init__(self, open_video_file_callback, open_pco_stream_callback):
        super().__init__()

        self.__central_layout = QHBoxLayout(self)
        self.__central_layout.setObjectName(u"central_layout")

        self.__groupbox_open_source = QGroupBox(self)
        self.__groupbox_open_source.setObjectName("groupbox")
        self.__groupbox_open_source.setTitle(u"Open Source")
        self.__central_layout.addWidget(self.__groupbox_open_source)

        self.__groupbox_open_source_layout = QHBoxLayout(self.__groupbox_open_source)
        self.__central_layout.setObjectName(u"__groupbox_open_source_layout")

        self.__open_video_file_button = QPushButton(self)
        self.__open_video_file_button.setObjectName(u"open_video_file_button")
        self.__open_video_file_button.setText("Open Video File")
        self.__open_video_file_button.clicked.connect(open_video_file_callback)
        self.__groupbox_open_source_layout.addWidget(self.__open_video_file_button)

        self.__open_camera_stream_button = QPushButton(self)
        self.__open_camera_stream_button.setObjectName(u"open_camera_stream_button")
        self.__open_camera_stream_button.setText(u"Open PCO Camera Stream")
        self.__open_camera_stream_button.clicked.connect(open_pco_stream_callback)
        self.__groupbox_open_source_layout.addWidget(self.__open_camera_stream_button)

        self.__groupbox_stream_control = QGroupBox(self)
        self.__groupbox_stream_control.setObjectName("groupbox")
        self.__groupbox_stream_control.setTitle(u"PCO Control")
        self.__groupbox_stream_control.setEnabled(False)
        self.__central_layout.addWidget(self.__groupbox_stream_control)

        self.__groupbox_stream_control_layout = QHBoxLayout(self.__groupbox_stream_control)
        self.__groupbox_stream_control_layout.setObjectName(u"groupbox_stream_control_layout")

        self.__start_stream_button = QPushButton(self)
        self.__start_stream_button.setObjectName(u"start_stream_button")
        self.__start_stream_button.setText(u"Start PCO Stream")
        self.__groupbox_stream_control_layout.addWidget(self.__start_stream_button)

        self.__stop_stream_button = QPushButton(self)
        self.__stop_stream_button.setObjectName(u"stop_stream_button")
        self.__stop_stream_button.setText(u"Stop PCO Stream")
        self.__groupbox_stream_control_layout.addWidget(self.__stop_stream_button)

        self.__groupbox_video_file_control = QGroupBox(self)
        self.__groupbox_video_file_control.setObjectName(u"groupbox_video_file_control")
        self.__groupbox_video_file_control.setTitle(u"Video File Control")
        self.__groupbox_video_file_control.setEnabled(False)
        self.__central_layout.addWidget(self.__groupbox_video_file_control)

        self.__groupbox_video_file_control_layout = QHBoxLayout(self.__groupbox_video_file_control)
        self.__groupbox_video_file_control_layout.setObjectName(u"groupbox_video_file_control_layout")

        self.__play_video_file_button = QPushButton(self)
        self.__play_video_file_button.setObjectName(u"play_video_file_button")
        self.__play_video_file_button.setText(u"Play Video")
        self.__groupbox_video_file_control_layout.addWidget(self.__play_video_file_button)

        self.__pause_video_file_button = QPushButton(self)
        self.__pause_video_file_button.setObjectName(u"pause_video_file_button")
        self.__pause_video_file_button.setText(u"Pause Video")
        self.__groupbox_video_file_control_layout.addWidget(self.__pause_video_file_button)

        self.__stop_video_file_button = QPushButton(self)
        self.__stop_video_file_button.setObjectName(u"stop_video_file_button")
        self.__stop_video_file_button.setText(u"Stop Video")
        self.__groupbox_video_file_control_layout.addWidget(self.__stop_video_file_button)

    def enable_video_controls(self):
        self.__groupbox_video_file_control.setEnabled(True)

    def disable_video_controls(self):
        self.__groupbox_video_file_control.setEnabled(False)

    def enable_stream_controls(self):
        self.__groupbox_stream_control.setEnabled(True)

    def disable_stream_controls(self):
        self.__groupbox_stream_control.setEnabled(False)