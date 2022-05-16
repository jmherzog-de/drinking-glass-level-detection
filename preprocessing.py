import threading
from pco_capture import *
import cv2 as cv
import numpy as np
from bv_algorithms import AutoscaleImage

diff_set = False
diff_img = np.zeros(shape=(2048, 2048), dtype=np.uint8)
frame_counter = 0
kernel = np.ones((5, 5), np.uint8)
bv_native_autoscale = AutoscaleImage()


def update_original_frame(image: np.ndarray):

    global diff_set, diff_img, frame_counter, bv_native_autoscale
    image = bv_native_autoscale.autoscale(image)
    image_8bit = cv.normalize(image, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U)
    image_8bit_f = image_8bit.astype('float64')
    # image_8bit_f = np.where(image_8bit_f > 250, 0, image_8bit_f)
    cv.imshow("Live Image", cv.resize(image_8bit, (1024, 1024)))

    if not diff_set:
        diff_img = image_8bit_f.copy()
        cv.imshow("Reference Image", cv.resize(diff_img.astype('uint8'), (1024, 1024)))
        diff_set = True
    elif frame_counter == 1:

        # Create difference image
        # Note: Either take pixels with a minimum difference over 80 and set them to 255 or keep
        # the new pixel value
        img = np.where(abs(image_8bit_f - diff_img) > 80, 255, 0)
        # img = np.where(abs(image_8bit_f - diff_img) > 80, image_8bit_f, 0)

        # Blur filter the image
        blur_img = cv.blur(img.astype('uint8'), (10, 10))

        # Sobel Y-Axis
        gray_y = cv.Sobel(blur_img, cv.CV_8U, 0, 1, ksize=3, scale=1, delta=0, borderType=cv.BORDER_DEFAULT)

        # Apply Adaptive Threshold
        thresh1 = cv.adaptiveThreshold(gray_y, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 6)

        # Apply fixed threshold
        _, thresh2 = cv.threshold(gray_y, thresh=50, maxval=255, type=cv.THRESH_BINARY)

        # Apply canny edge detection
        canny = cv.Canny(gray_y, threshold1=50, threshold2=150, edges=None, apertureSize=3, L2gradient=False)

        # Find Contours in image
        contours, hierarchy = cv.findContours(thresh1, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        contours_image = np.zeros(shape=(2048, 2048), dtype='uint8')
        cv.drawContours(contours_image, contours, -1, (255, 255, 255), 3)

        cv.imshow("Difference Image", cv.resize(img.astype('uint8'), (1024, 1024)))
        cv.imshow("Sobel Y", cv.resize(gray_y, (1024, 1024)))
        cv.imshow("Adaptive Threshold", cv.resize(thresh1, (1024, 1024)))
        cv.imshow("Threshold", cv.resize(blur_img, (1024, 1024)))
        cv.imshow("Canny", cv.resize(canny, (1024, 1024)))
        cv.imshow("Contours", cv.resize(contours_image, (1024, 1024)))

        frame_counter = 0
    else:
        frame_counter += 1

    cv.waitKey(1)


if __name__ == '__main__':
    capture = VideoCapture(frame_available_callback=update_original_frame)
    capture_thread = threading.Thread(target=capture.run)
    capture_thread.start()
    capture_thread.join()
    exit(0)
