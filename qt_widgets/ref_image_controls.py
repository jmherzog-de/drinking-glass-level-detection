from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout


class ReferenceImageControlsWidget(QWidget):

    def __init__(self, save_ref_image_callback):
        super().__init__()
        self.__save_ref_image_callback = save_ref_image_callback

        self.central_layout = QHBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        self.save_ref_image_button = QPushButton()
        self.save_ref_image_button.setObjectName(u"save_ref_image_button")
        self.save_ref_image_button.setText(u"Save as Reference Image")
        self.central_layout.addWidget(self.save_ref_image_button)
