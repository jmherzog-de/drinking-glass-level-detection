import pco
import os
import cv2
from datetime import datetime
from PySide6.QtCore import QThread, Signal
import numpy as np


class VideoCapture(object):
    """
    Video capture class from PCO camera.
    """

    def __init__(self, frame_available_callback):
        """
        Constructor
        :param frame_available_callback: callback event for new frame from camera available.
        """
        self.__frame_available_callback = frame_available_callback
        self.cam = pco.Camera()
        self.__frame_counter = 0

    def run(self):
        """
        Start capture from camera.
        :return: None
        """
        # --------------------------------------------- #
        # Setup Camera Parameters                       #
        # --------------------------------------------- #
        self.cam.set_exposure_time(0.01)

        # --------------------------------------------- #
        # Start recording
        # --------------------------------------------- #
        self.cam.record(number_of_images=40, mode='fifo')
        while True:
            self.cam.wait_for_first_image()
            image, _ = self.cam.image()
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

            if self.__frame_counter == 2:
                self.__frame_counter = 0
                self.__frame_available_callback(image)
            else:
                self.__frame_counter += 1


class QtVideoCapture(QThread):
    """
    Video capture class with Qt QThread implementation.
    """

    # Callback signal when new frame available from camera.
    update_frame = Signal(np.ndarray)

    def __init__(self):
        """
        Constructor
        """
        QThread.__init__(self, parent=None)
        self.capture_enabled = False
        self.save_image = False
        self.__captured_images = []
        self.__counter = 0

    def run(self):
        """
        Start capture process from camera.
        :return: None
        """

        with pco.Camera() as cam:

            # --------------------------------------------- #
            # Setup Camera Parameters                       #
            # --------------------------------------------- #
            cam.set_exposure_time(0.01)  # 0.014997

            # --------------------------------------------- #
            # Create folder on local system to save all     #
            # captured images from camera.                  #
            # --------------------------------------------- #
            if self.save_image:
                folder_name = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                os.mkdir(folder_name)

            # --------------------------------------------- #
            # Start recording
            # --------------------------------------------- #
            cam.record(number_of_images=40, mode='fifo')

            while self.capture_enabled:

                cam.wait_for_first_image()
                image, _ = cam.image()
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

                if self.__counter == 2:
                    if self.save_image:
                        self.__captured_images.append(image)
                    self.update_frame.emit(image)
                    self.__counter = 0
                else:
                    self.__counter += 1

            # END OF CAPTURE PROCESS
            if self.save_image:
                print("Save images on filesystem...")
                n = len(self.__captured_images)
                counter = 0
                while len(self.__captured_images) > 0:
                    image = self.__captured_images.pop()
                    cv2.imwrite(f"{folder_name}/capture_{counter}.png", image)
                    counter += 1
                    print(f"({counter+1}/{n})")
                print("all images saved.")

            cam.close()

