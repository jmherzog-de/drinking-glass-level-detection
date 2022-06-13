import cv2
import numpy as np


class GlasDetection(object):

    def __init__(self):

        # private variables
        self.__detected: bool = False
        self.__ref_contour: tuple = (0, 0, 0, 0)
        self.__cycle_counter: int = 0

        # public variables
        self.abs_pixel_tolerance: int = 10
        self.detection_cycles: int = 30

    def detect(self, frame: np.ndarray):

        if self.__detected:
            return

        frame = cv2.blur(frame, (3, 3), cv2.BORDER_DEFAULT)
        frame = cv2.Canny(frame, 10, 200)
        frame = cv2.dilate(frame, np.ones((5, 5), np.uint8), 8)
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            self.__cycle_counter = 0

        biggest_contour = (0, 0, 0, 0)
        biggest_area = 0
        for contour in contours:
            if cv2.contourArea(contour) > biggest_area:
                biggest_contour = cv2.boundingRect(contour)

        diff = tuple(map(lambda x, y: abs(x-y), self.__ref_contour, biggest_contour))
        if max(diff) > self.abs_pixel_tolerance:
            self.__ref_contour = biggest_contour
            self.__cycle_counter = 0
        else:
            self.__cycle_counter += 1

        if self.__cycle_counter >= self.detection_cycles:
            self.__detected = True

        return

    def state(self):
        return self.__detected

    def estimated_glas(self):
        if self.__cycle_counter == (0, 0, 0, 0):
            return None, None, None, None
        else:
            return self.__ref_contour[0], self.__ref_contour[1], self.__ref_contour[0] + self.__ref_contour[2], \
                   self.__ref_contour[1] + self.__ref_contour[3]

    def reset_detection(self):
        self.__detected = False
        self.__ref_contour = (0, 0, 0, 0)


def level_detection(frame: np.ndarray):

    kernel = np.ones((5, 5), np.uint8)

    frame = cv2.erode(frame, kernel, 2)
    frame = cv2.dilate(frame, kernel, 3)

    contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

    for cnt in contours:
        cnt_area = cv2.contourArea(cnt)
        if cnt_area > 450:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)

    return frame


def difference_image(ref_frame: np.ndarray, frame: np.ndarray, distance: int):

    diff_image = abs(frame.astype('float64') - ref_frame.astype('float64'))
    diff_image = np.where(diff_image >= distance, 255, 0)
    diff_image = diff_image.astype('uint8')
    return diff_image
