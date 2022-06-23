import cv2
import numpy as np


class GlassDetection(object):

    def __init__(self):

        # private variables
        self.__detected: bool = False
        self.__ref_contour: tuple = (0, 0, 0, 0)
        self.__cycle_counter: int = 0
        self.__stencil_frame: np.ndarray = None
        self.__mask_frame: np.ndarray = None
        self.__stencil_contours_frame = None
        self.__glas_frame: np.ndarray = None
        self.__detected_glass_type: int = -1    # 0: small glass 1: big glass -1: no glass

        # public variables
        self.abs_pixel_tolerance: int = 10
        self.detection_cycles: int = 30
        self.mask_offset_top: float = 0.1
        self.mask_offset_bottom: float = 0.1
        self.mask_offset_left: float = 0.0
        self.mask_offset_right: float = 0.0
        self.large_glass_size: (int, int) = (480, 1280)
        self.small_glass_size: (int, int) = (480, 1040)

    def create_stencil(self, frame: np.ndarray):

        # Extract height and width of the detected glas BoundingBox
        (height, width) = self.__ref_contour[3], self.__ref_contour[2]

        # Create a mask with all black pixels
        self.__stencil_frame = np.full(shape=(height, width), fill_value=0, dtype='uint8')

        # Get contours of within the glas BoundingBox
        range_y = range(height)
        self.__stencil_contours_frame = np.zeros(frame.shape)
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 450:
                cv2.drawContours(self.__stencil_contours_frame, cnt, -1, (255, 255, 255), 1)
                self.__stencil_frame = cv2.fillPoly(self.__stencil_frame, pts=[cnt], color=(255, 255, 255))

        # cv2.imshow("STENCIL_CONTOUR", self.__stencil_contours_frame)
        # cv2.waitKey(1)

        # Repair broken edge detection of the glass.
        # Note: This appears mainly at the above part of the glass.

        # 1. Close holes with morphological filters
        self.__stencil_frame = cv2.dilate(self.__stencil_frame, np.ones((31, 31), np.uint8), 1)

        # 2. Close cylinder contour of the glass
        # Note: Based on the mean of each edge-side...
        (mean_right, mean_left, n_mean_left, n_mean_right) = (0, 0, 0, 0)

        # Iterate all lines
        for yi in range_y:
            t = np.where(self.__stencil_frame[yi][0:-1] == 255)     # Extract all pixels of the glas

            if len(t) > 0 and len(t[0]) > 0:
                # Extract left first edge and right first edge
                t1 = t[0][0]
                t2 = t[0][-1]

                if int(height * 0.1) < yi < int(height - height * 0.1):
                    if abs(t2 - self.__ref_contour[2]) < self.__ref_contour[2]*0.05:
                        n_mean_right += 1
                        mean_right += t2
                    if t1 < self.__ref_contour[3]*0.05:
                        n_mean_left += 1
                        mean_left += t1
                self.__stencil_frame[yi][t1:t2] = 255   # Fill all pixels between left and right edge

        mean_right = mean_right / n_mean_right
        mean_left = mean_left / n_mean_left

        # 3. Reconstruct cylinder contour for failed contour detection.
        # Note: Mean pixel position used to determine the approximated right place for the edge pixel
        range_y = range(int(height*0.1), int(height-(height*0.1)), 1)   # Ignore 10 % of the height from top and bottom
        for yi in range_y:
            t = np.where(self.__stencil_frame[yi][0:-1] == 255)
            if len(t) > 0 and len(t[0]) > 0:
                t1 = t[0][0]
                t2 = t[0][-1]

                if mean_right - t2 > 0:
                    self.__stencil_frame[yi][t1:int(mean_right)] = 255
                if t1 - mean_left > 0:
                    self.__stencil_frame[yi][int(mean_left):t2] = 255

        self.__mask_frame = self.__stencil_frame.copy()
        for yi in range(0, int(height * self.mask_offset_top)):
            self.__mask_frame[yi] = 0
        for yi in range(int(height-height * self.mask_offset_bottom), height):
            self.__mask_frame[yi] = 0

        self.__stencil_frame = cv2.cvtColor(self.__stencil_frame, cv2.COLOR_GRAY2RGB)
        for yi in range_y:
            cv2.circle(self.__stencil_frame, (int(mean_right), yi), 0, (255, 0, 0), 2)
            cv2.circle(self.__stencil_frame, (int(mean_left), yi), 0, (255, 0, 0), 2)

        for xi in range(width):
            cv2.circle(self.__stencil_frame, (xi, int(height*0.1)), 0, (0, 255, 255), 2)
            cv2.circle(self.__stencil_frame, (xi, int(height-height * 0.1)), 0, (0, 255, 255), 2)

        # cv2.imshow("IMAGE", self.__mask_frame)
        # cv2.waitKey(1)

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
        _, frame = cv2.threshold(weighted, 40, 255, cv2.THRESH_BINARY)

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

            # Check if the determined contour could be the small or large glass
            estimated_height = self.__ref_contour[3]
            estimated_width = self.__ref_contour[2]
            estimated_size = (estimated_width, estimated_height)

            pos_offset = tuple(map(lambda i, j: abs(i-j), estimated_size, self.small_glass_size))
            pos_offset = tuple(map(lambda i, j: i <= 0.1*j, pos_offset, self.small_glass_size))
            if pos_offset == (True, True):
                self.__detected_glass_type = 0

            pos_offset = tuple(map(lambda i, j: abs(i-j), estimated_size, self.large_glass_size))
            pos_offset = tuple(map(lambda i, j: i <= 0.1*j, pos_offset, self.large_glass_size))
            if pos_offset == (True, True):
                self.__detected_glass_type = 1

            if self.__detected_glass_type == -1:
                self.__cycle_counter = 0
            else:
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

    def get_glas_mask(self):
        return self.__mask_frame

    def get_glas_frame(self):
        return self.__glas_frame

    def get_detected_glass_type(self):
        return self.__detected_glass_type

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
        self.__glass_mask: np.ndarray = None
        self.__current_level_pixel: int = 0

    def detect(self, frame: np.ndarray):

        if self.__glass_mask is None:
            return frame

        frame = cv2.bitwise_and(self.__glass_mask, frame)

        kernel = np.ones((7, 7), np.uint8)
        frame = cv2.erode(frame, kernel, 1)
        kernel = np.ones((13, 13), np.uint8)
        frame = cv2.dilate(frame, kernel, 1)

        cv2.imshow("LEVEL_DETECTOR", frame)
        cv2.waitKey(1)

        grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        _, frame = cv2.threshold(abs_grad_y, 30, 255, cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        for cnt in contours:
            cnt_area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            if cnt_area > 450 and 1.5 * w > h:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)

        return frame

    def set_glass_mask(self, mask: np.ndarray):
        self.__glass_mask = mask.copy()


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
