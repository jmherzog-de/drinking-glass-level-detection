import cv2
import sys
import numpy as np


class GlassDetection(object):
    """
    Class bundle features for a simple glass detection.
    """

    def __init__(self):
        """
        Class constructor method for GlassDetection.
        """

        # Detect if application runs in debug mode or not
        # Note: Additional information will be displayed in Debug mode.
        self.__debug_mode = (gettrace := getattr(sys, 'gettrace')) and gettrace()

        # Glass detected flag.
        self.__detected: bool = False

        # Reference contour.
        self.__ref_contour: tuple = (0, 0, 0, 0)

        # Cycle counter found the same contour for estimated glass.
        self.__cycle_counter: int = 0

        # Binarized glass mask - This contains the whole glass.
        self.__stencil_frame: np.ndarray = None

        # Binarized detection area of the glass.
        self.__mask_frame: np.ndarray = None

        # Contains the detected contours for the glass mask.
        self.__stencil_contours_frame = None

        # Original image with full size estimated glass.
        self.__glass_frame: np.ndarray = None

        # 0: small glass 1: big glass -1: no glass
        self.__detected_glass_type: int = -1

        # Tolerance for generating glass mask contours left and right.
        self.abs_pixel_tolerance: int = 10

        # Number of cycles with constant estimated glass before the glass detection process
        # gets marked as done
        self.detection_cycles: int = 30

        # Top offset for the mask_frame. (Default 10 %)
        self.mask_offset_top: float = 0.1

        # Bottom offset for the mask_frame (Default 10 %)
        self.mask_offset_bottom: float = 0.1

        # Reference size in pixel of the large glass.
        self.large_glass_size: (int, int) = (480, 1280)

        # Reference size in pixel of the small glass.
        self.small_glass_size: (int, int) = (480, 1040)

    def create_stencil(self, frame: np.ndarray):
        """
        Create binarized glass mask from estimated glass.
        Note: This method need a frame only containing the area of the estimated glass. Not the original
        frame from the camera.

        :param frame: frame contain estimated glass section.
        :return: None
        """

        # Modify mask offset for small glass.
        if self.__detected_glass_type == 0:
            self.mask_offset_top = 0.2

        # Extract height and width of the detected glass BoundingBox
        (height, width) = self.__ref_contour[3], self.__ref_contour[2]

        # Create a mask with all black pixels
        self.__stencil_frame = np.full(shape=(height, width), fill_value=0, dtype='uint8')

        # Get contours of within the glass BoundingBox
        range_y = range(height)
        self.__stencil_contours_frame = np.zeros(frame.shape)
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 450:
                cv2.drawContours(self.__stencil_contours_frame, cnt, -1, (255, 255, 255), 1)
                self.__stencil_frame = cv2.fillPoly(self.__stencil_frame, pts=[cnt], color=(255, 255, 255))

        if self.__debug_mode:
            cv2.imshow("STENCIL_CONTOUR", self.__stencil_contours_frame)
            cv2.waitKey(1)

        # Repair broken edge detection of the glass.
        # Note: This appears mainly at the above part of the glass.

        # 1. Close holes with morphological filters
        self.__stencil_frame = cv2.dilate(self.__stencil_frame, np.ones((31, 31), np.uint8), 1)

        # 2. Close cylinder contour of the glass
        # Note: Based on the mean of each edge-side...
        (mean_right, mean_left, n_mean_left, n_mean_right) = (0, 0, 0, 0)

        # Iterate all lines
        for yi in range_y:
            t = np.where(self.__stencil_frame[yi][0:-1] == 255)     # Extract all pixels of the glass

            if len(t) > 0 and len(t[0]) > 0:
                # Extract left first edge and right first edge
                t1 = t[0][0]
                t2 = t[0][-1]

                if int(height * self.mask_offset_top) < yi < int(height - height * self.mask_offset_bottom):
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

        if self.__debug_mode:
            cv2.imshow("IMAGE", self.__mask_frame)
            cv2.waitKey(1)

        return

    def detect(self, frame: np.ndarray):
        """
        Perform glass detection on the given input frame.

        :param frame: Original image frame from camera.
        :return: blurred frame
        """

        # ------------------------------------------------- #
        # 1. Blur input frame before further processing
        # ------------------------------------------------- #
        orig_frame = frame.copy()
        frame = cv2.blur(frame, (7, 7), cv2.BORDER_DEFAULT)

        # ------------------------------------------------- #
        # 2. Sobel Operator to detect glass contour
        # ------------------------------------------------- #
        grad_x = cv2.Sobel(frame, cv2.CV_16S, 1, 0, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)

        # ------------------------------------------------- #
        # 3. Transform into 8-bit pixel values.
        # ------------------------------------------------- #
        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)

        # ------------------------------------------------- #
        # 4. Overlay x and y Sobel components
        # ------------------------------------------------- #
        weighted = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

        # ------------------------------------------------- #
        # 5. Threshold resulting image with static values.
        # ------------------------------------------------- #
        _, frame = cv2.threshold(weighted, 40, 255, cv2.THRESH_BINARY)

        # ------------------------------------------------- #
        # 6. Make a copy of the estimated glass section.
        # ------------------------------------------------- #
        if self.__detected:
            self.__glass_frame = orig_frame[
                                self.__ref_contour[1]:self.__ref_contour[1] + self.__ref_contour[3],
                                self.__ref_contour[0]:self.__ref_contour[0] + self.__ref_contour[2]]
            return frame.copy()

        # ------------------------------------------------- #
        # 7. Detect contours in binarized image.
        # ------------------------------------------------- #
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # ------------------------------------------------- #
        # 8. Estimate glass with checking the largest contour.
        # ------------------------------------------------- #
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
                self.__glass_frame = orig_frame[
                                    self.__ref_contour[1]:self.__ref_contour[1] + self.__ref_contour[3],
                                    self.__ref_contour[0]:self.__ref_contour[0] + self.__ref_contour[2]]

                self.create_stencil(frame[
                                    self.__ref_contour[1]:self.__ref_contour[1] + self.__ref_contour[3],
                                    self.__ref_contour[0]:self.__ref_contour[0] + self.__ref_contour[2]])

        return frame.copy()

    def state(self):
        """
        Glass detection state.
        :return: True: Glass detected | False: Glass not detected
        """
        return self.__detected

    def get_glass_stencil(self):
        """
        Binarized estimated glass area.
        :return: frame with estimated glass area in white pixels (background black)
        """
        return self.__stencil_frame

    def get_glass_mask(self):
        """
        Binarized estimated filling area of the glass.
        This image doesn't contain the top and bottom of the glass mask.
        :return: frame with estimated filling area of the glass
        """
        return self.__mask_frame

    def get_glass_frame(self):
        """
        Frame contain the estimated glass area from the camera.
        :return: Estimated glass frame
        """
        return self.__glass_frame

    def get_detected_glass_type(self):
        """
        Type of the detected glass.
        Currently there are two types implemented.
        :return: 0: Small glass | 1: Large glass | -1: No glass
        """
        return self.__detected_glass_type

    def estimated_glass(self):
        """
        Position of the estimated glass BoundingBox.
        :return: Tuple (x1, y1, x2, y2)
        """
        if self.__cycle_counter == (0, 0, 0, 0):
            return None, None, None, None
        else:
            return self.__ref_contour[0], self.__ref_contour[1], self.__ref_contour[0] + self.__ref_contour[2], \
                   self.__ref_contour[1] + self.__ref_contour[3]

    def reset_detection(self):
        """
        Reset detection state.
        :return: None
        """
        self.__detected = False
        self.__ref_contour = (0, 0, 0, 0)


class LevelDetector(object):
    """
    Class for fill-level-detection
    """

    def __init__(self):
        """
        Constructor method.
        """

        # Detect if application runs in debug mode or not
        # Note: Additional information will be displayed in Debug mode.
        self.__debug_mode = (gettrace := getattr(sys, 'gettrace')) and gettrace()

        # Glass filling area mask
        self.__glass_mask: np.ndarray = None

        # Current filling level in pixel
        # Note: Pixel position on y-Axis will be stored in this variable.
        self.__current_level_pixel: int = 0

        # All detection lines to calculate fill-level
        self.__detection_lines = []

    def detect(self, frame: np.ndarray):
        """
        Detect current fill-level for the input frame.

        :param frame: Frame contain only the estimated glass area. Not the whole camera frame.
        :return: None
        """

        if self.__glass_mask is None:
            return frame

        # -------------------------------------------------------------- #
        # 1. Generate detection lines
        # -------------------------------------------------------------- #
        (height, width) = frame.shape
        if len(self.__detection_lines) == 0:
            self.__detection_lines.append((int(0.1*width), 0, int(0.1*width), height))
            self.__detection_lines.append((int(0.2 * width), 0, int(0.2 * width), height))
            self.__detection_lines.append((int(0.3 * width), 0, int(0.3 * width), height))
            self.__detection_lines.append((int(0.4 * width), 0, int(0.4 * width), height))
            self.__detection_lines.append((int(0.5 * width), 0, int(0.5 * width), height))
            self.__detection_lines.append((int(0.6 * width), 0, int(0.6 * width), height))
            self.__detection_lines.append((int(0.7 * width), 0, int(0.7 * width), height))
            self.__detection_lines.append((int(0.8 * width), 0, int(0.8 * width), height))
            self.__detection_lines.append((int(0.9 * width), 0, int(0.9 * width), height))

        # -------------------------------------------------------------- #
        # 2. Eliminate all unimportant pixels
        # Note: This generate a binarized image.
        # -------------------------------------------------------------- #
        frame = cv2.bitwise_and(self.__glass_mask, frame)

        # -------------------------------------------------------------- #
        # 3. Process the resulting image by using Morphological Filters
        # Note: This should stabilize the binarized image.
        # -------------------------------------------------------------- #
        kernel = np.ones((7, 7), np.uint8)
        frame = cv2.erode(frame, kernel, 2)
        kernel = np.ones((13, 13), np.uint8)
        frame = cv2.dilate(frame, kernel, 1)

        if self.__debug_mode:
            cv2.imshow("LEVEL_DETECTOR", frame)
            cv2.waitKey(1)

        # -------------------------------------------------------------- #
        # 4. Filling level detection
        # Note: Use Sobel operator along the horizontal axis to estimate
        # the contour of the filling level.
        # -------------------------------------------------------------- #
        grad_y = cv2.Sobel(frame, cv2.CV_16S, 0, 1, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        _, frame = cv2.threshold(abs_grad_y, 30, 255, cv2.THRESH_BINARY)
        frame = cv2.dilate(frame, kernel, 1)

        # Detect first pixels on detection line from top to bottom
        detected_heights = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        # Find first and second detection line
        for yi in range(height):
            if frame[yi][int(0.1*width)] == 255 and detected_heights[0] == 0:
                detected_heights[0] = yi
            if frame[yi][int(0.2*width)] == 255 and detected_heights[1] == 0:
                detected_heights[1] = yi
            if frame[yi][int(0.3*width)] == 255 and detected_heights[2] == 0:
                detected_heights[2] = yi
            if frame[yi][int(0.4*width)] == 255 and detected_heights[3] == 0:
                detected_heights[3] = yi
            if frame[yi][int(0.5*width)] == 255 and detected_heights[4] == 0:
                detected_heights[4] = yi
            if frame[yi][int(0.6*width)] == 255 and detected_heights[5] == 0:
                detected_heights[5] = yi
            if frame[yi][int(0.7*width)] == 255 and detected_heights[6] == 0:
                detected_heights[6] = yi
            if frame[yi][int(0.8*width)] == 255 and detected_heights[7] == 0:
                detected_heights[7] = yi
            if frame[yi][int(0.9*width)] == 255 and detected_heights[8] == 0:
                detected_heights[8] = yi

        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        # Draw estimated fill-level line
        self.__current_level_pixel = int(sum(detected_heights) / len(detected_heights))
        cv2.line(frame, pt1=(0, self.__current_level_pixel), pt2=(width, self.__current_level_pixel),
                 color=(0, 0, 255), thickness=3)

        # Draw detection lines
        for detection_line in self.__detection_lines:
            cv2.line(frame, pt1=(detection_line[0], detection_line[1]), pt2=(detection_line[2], detection_line[3]),
                     color=(0, 255, 0), thickness=2)

        return frame

    def set_glass_mask(self, mask: np.ndarray):
        """
        Update the glass mask.
        :param mask: new binarized mask.
        :return: None
        """
        self.__glass_mask = mask.copy()

    def get_current_level(self):
        """
        Get the current fill level in pixel.
        Note: This method return the pixel value referenced by
        the mask image. To get the 'real' level in pixel on the original frame, there have to be converted.
        :return: Fill level in pixel
        """
        return self.__current_level_pixel


class DifferenceImageBuilder(object):
    """
    Class to build a difference image
    """

    def __init__(self):
        """
        Constructor
        """

        # Detect if application runs in debug mode or not
        # Note: Additional information will be displayed in Debug mode.
        self.__debug_mode = (gettrace := getattr(sys, 'gettrace')) and gettrace()

        # Reference image
        self.__ref_image = None

        # Resulting difference image
        self.__diff_image = None

        # Threshold distance between reference image and difference image
        self.distance: int = 10

    def build(self, frame: np.ndarray):
        """
        This method create a binarized difference image from the input frame and a internal saved reference frame.
        :param frame: Input frame
        :return: None
        """
        self.__diff_image = abs(frame.astype('float64') - self.__ref_image.astype('float64'))
        self.__diff_image = np.where(self.__diff_image >= self.distance, 255, 0)
        self.__diff_image = self.__diff_image.astype('uint8')
        return self.__diff_image

    def set_reference_image(self, frame: np.ndarray):
        """
        Update reference image with the input image of this method.
        :param frame: New reference image
        :return: None
        """
        self.__ref_image = frame.copy()
