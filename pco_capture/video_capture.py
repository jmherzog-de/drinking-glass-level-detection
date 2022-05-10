import pco
import cv2 as cv


class VideoCapture(object):

    def __init__(self, frame_available_callback):
        self.__frame_available_callback = frame_available_callback
        self.cam = pco.Camera()
        self.__frame_counter = 0

    def run(self):
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
            image = cv.rotate(image, cv.ROTATE_90_CLOCKWISE)

            if self.__frame_counter == 2:
                self.__frame_counter = 0
                self.__frame_available_callback(image)
            else:
                self.__frame_counter += 1