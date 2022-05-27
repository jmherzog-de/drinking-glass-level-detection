from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QPushButton, QLineEdit


class ROIWidget(QWidget):

    def __init__(self, roi_selected_callback):
        super().__init__()
        self.__roi_selected_callback = roi_selected_callback

        self.central_layout = QVBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        self.groupbox_controls = QGroupBox()
        self.groupbox_controls.setObjectName(u"groupbox_controls")
        self.groupbox_controls.setTitle(u"Select ROI Coordinates")
        self.central_layout.addWidget(self.groupbox_controls)

        self.roi_form_layout = QFormLayout(self.groupbox_controls)
        self.roi_form_layout.setObjectName(u"roi_form_layout")

        self.roi_text_edit_x1 = QLineEdit()
        self.roi_text_edit_x1.setObjectName(u"roi_text_edit_x1")
        self.roi_text_edit_x1.setText(u"0")
        self.roi_form_layout.addRow("x_1:", self.roi_text_edit_x1)

        self.roi_text_edit_y1 = QLineEdit()
        self.roi_text_edit_y1.setObjectName(u"roi_text_edit_y1")
        self.roi_text_edit_y1.setText(u"0")
        self.roi_form_layout.addRow("y_1:", self.roi_text_edit_y1)

        self.roi_text_edit_x2 = QLineEdit()
        self.roi_text_edit_x2.setObjectName(u"roi_text_edit_x2")
        self.roi_text_edit_x2.setText(u"2048")
        self.roi_form_layout.addRow("x_2:", self.roi_text_edit_x2)

        self.roi_text_edit_y2 = QLineEdit()
        self.roi_text_edit_y2.setObjectName(u"roi_text_edit_y2")
        self.roi_text_edit_y2.setText(u"2048")
        self.roi_form_layout.addRow("y_2:", self.roi_text_edit_y2)

        self.select_button = QPushButton()
        self.select_button.setObjectName(u"select_button")
        self.select_button.setText(u"Select ROI")
        self.select_button.clicked.connect(self.__roi_selected_callback)
        self.central_layout.addWidget(self.select_button)
