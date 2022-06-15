import cv2
import numpy as np


class GlasDetection(object):

    def __init__(self):

        # private variables
        self.__detected: bool = False
        self.__ref_contour: tuple = (0, 0, 0, 0)
        self.__cycle_counter: int = 0
        self.__stencil_frame: np.ndarray = None
        self.__glas_frame: np.ndarray = None

        # public variables
        self.abs_pixel_tolerance: int = 10
        self.detection_cycles: int = 30

    def create_stencil(self, frame: np.ndarray):

        height = self.__ref_contour[3]
        width = self.__ref_contour[2]
        self.__stencil_frame = np.full(shape=(height, width), fill_value=255, dtype='uint8')
        range_x = range(width)
        range_y = range(height)

        # find left and right edge of the glas
        for yi in range_y:
            t = np.where(frame[yi] > 0)
            if len(t) > 0 and len(t[0]) > 0:
                t1 = t[0][0]
                t2 = t[0][-1]
            self.__stencil_frame[yi][t1] = 0
            self.__stencil_frame[yi][t2] = 0

        # find top edge of the glas
        for xi in range_x:
            for yi in range_y:
                if frame[yi][xi] > 0:
                    self.__stencil_frame[yi][xi] = 0
                    break
                else:
                    self.__stencil_frame[yi][xi] = 0
            for yi in reversed(range_y):
                if frame[yi][xi] > 0:
                    self.__stencil_frame[yi][xi] = 0
                    break
                else:
                    self.__stencil_frame[yi][xi] = 0
        self.__stencil_frame = cv2.erode(self.__stencil_frame, np.ones((9, 9), np.uint8), 1)

        return

    def detect(self, frame: np.ndarray):

        orig_frame = frame.copy()
        frame = cv2.blur(frame, (7, 7), cv2.BORDER_DEFAULT)

        #
        # Image Processing with Sobel Operator
        #
        grad_x = cv2.Sobel(frame, cv2.CV_16S, 1, 0, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)

        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        weighted = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
        _, frame = cv2.threshold(weighted, 40, 100, cv2.THRESH_BINARY)

        frame = cv2.dilate(frame, (7, 7), 7)

        if self.__detected:
            self.__glas_frame = orig_frame[
                                self.__ref_contour[1]:self.__ref_contour[1] + self.__ref_contour[3],
                                self.__ref_contour[0]:self.__ref_contour[0] + self.__ref_contour[2]]
            return frame.copy()

        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            self.__cycle_counter = 0

        biggest_contour = (0, 0, 0, 0)
        biggest_area = 0
        for contour in contours:
            if cv2.contourArea(contour) > biggest_area:
                biggest_contour = cv2.boundingRect(contour)

        diff = tuple(map(lambda x, y: abs(x - y), self.__ref_contour, biggest_contour))
        if max(diff) > self.abs_pixel_tolerance:
            self.__ref_contour = biggest_contour
            self.__cycle_counter = 0
        else:
            self.__cycle_counter += 1

        if self.__cycle_counter >= self.detection_cycles:
            self.__detected = True
            self.__glas_frame = orig_frame[
                                self.__ref_contour[1]:self.__ref_contour[1] + self.__ref_contour[3],
                                self.__ref_contour[0]:self.__ref_contour[0] + self.__ref_contour[2]]

            self.create_stencil(frame[
                                self.__ref_contour[1]:self.__ref_contour[1] + self.__ref_contour[3],
                                self.__ref_contour[0]:self.__ref_contour[0] + self.__ref_contour[2]])

        return frame.copy()

    def state(self):
        return self.__detected

    def get_glas_stencil(self):
        return self.__stencil_frame

    def get_glas_frame(self):
        return self.__glas_frame

    def estimated_glas(self):
        if self.__cycle_counter == (0, 0, 0, 0):
            return None, None, None, None
        else:
            return self.__ref_contour[0], self.__ref_contour[1], self.__ref_contour[0] + self.__ref_contour[2], \
                   self.__ref_contour[1] + self.__ref_contour[3]

    def reset_detection(self):
        self.__detected = False
        self.__ref_contour = (0, 0, 0, 0)


class LevelDetector(object):

    def __init__(self):
        self.__glas_stencil = None

    def detect(self, frame: np.ndarray):

        if self.__glas_stencil is None:
            return frame

        frame = cv2.bitwise_and(self.__glas_stencil, frame)

        kernel = np.ones((7, 7), np.uint8)
        frame = cv2.erode(frame, kernel, 3)
        # frame = cv2.dilate(frame, kernel, 3)

        grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        _, frame = cv2.threshold(abs_grad_y, 40, 100, cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        for cnt in contours:
            cnt_area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            if cnt_area > 450 and 1.5 * w > h:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
        return frame

    def set_glas_stencil(self, stencil: np.ndarray):
        self.__glas_stencil = stencil.copy()


class DifferenceImageBuilder(object):

    def __init__(self):
        self.__ref_image = None
        self.__diff_image = None

        self.distance: int = 10

    def build(self, frame: np.ndarray):
        self.__diff_image = abs(frame.astype('float64') - self.__ref_image.astype('float64'))
        self.__diff_image = np.where(self.__diff_image >= self.distance, 255, 0)
        self.__diff_image = self.__diff_image.astype('uint8')
        return self.__diff_image

    def set_reference_image(self, frame: np.ndarray):
        self.__ref_image = frame.copy()
