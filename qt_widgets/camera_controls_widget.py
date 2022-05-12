from PySide6.QtWidgets import QWidget, QGroupBox, QPushButton, QHBoxLayout, QCheckBox


class CameraControlsWidget(QWidget):

    def __init__(self, start_trig_event, stop_trig_event):
        super().__init__()

        self.__central_layout = QHBoxLayout(self)
        self.__central_layout.setObjectName(u"central_layout")

        self.__groupbox = QGroupBox(self)
        self.__groupbox.setObjectName("groupbox")
        self.__groupbox.setTitle("Camera Control")

        self.__central_layout.addWidget(self.__groupbox)

        self.__groupbox_layout = QHBoxLayout(self.__groupbox)
        self.__groupbox_layout.setObjectName(u"groupbox_layout")

        self.__start_button = QPushButton(self)
        self.__start_button.setObjectName("start_button")
        self.__start_button.setText("START")
        self.__start_button.clicked.connect(start_trig_event)

        self.__stop_button = QPushButton(self)
        self.__stop_button.setObjectName("stop_button")
        self.__stop_button.setText("STOP")
        self.__stop_button.clicked.connect(stop_trig_event)

        self.__save_checkbox = QCheckBox(self)
        self.__save_checkbox.setObjectName(u"save_images")
        self.__save_checkbox.setText("Save images.")

        self.__groupbox_layout.addWidget(self.__start_button)
        self.__groupbox_layout.addWidget(self.__stop_button)
        self.__groupbox_layout.addWidget(self.__save_checkbox)

    def disable_start_button(self):
        self.__start_button.setEnabled(False)
        self.__stop_button.setEnabled(True)

    def enable_start_button(self):
        self.__start_button.setEnabled(True)
        self.__stop_button.setEnabled(False)

    def get_checked_state(self):
        return self.__save_checkbox.checkState()
