import threading
from pco_capture import *
import cv2 as cv
import numpy as np
from bv_native_helpers import NativeAutoscale

diff_set = False
diff_img = np.zeros(shape=(2048, 2048), dtype=np.uint8)
frame_counter = 0
kernel = np.ones((5, 5), np.uint8)
bv_native_autoscale = NativeAutoscale()


def update_original_frame(image: np.ndarray):

    global diff_set, diff_img, frame_counter, bv_native_autoscale

    image = bv_native_autoscale.autoscale(image)
    image_8bit = cv.normalize(image, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U)
    image_8bit_f = image_8bit.astype('float64')
    # image_8bit_f = np.where(image_8bit_f > 250, 0, image_8bit_f)
    cv.imshow("Live Bild", cv.resize(image_8bit), (1024, 1024))

    if not diff_set:
        diff_img = image_8bit_f.copy()
        cv.imshow("REFERENZ BILD", cv.resize(diff_img.astype('uint8'), (1024, 1024)))
        diff_set = True
    elif frame_counter == 1:
        img = np.where(abs(image_8bit_f - diff_img) > 80, image_8bit_f, 0)
        blur_img = cv.blur(img.astype('uint8'), (10, 10))
        gray_y = cv.Sobel(blur_img, cv.CV_8U, 0, 1, ksize=3, scale=1, delta=0, borderType=cv.BORDER_DEFAULT)
        thresh1 = cv.adaptiveThreshold(gray_y, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 6)
        cv.imshow("Y-Kanten", cv.resize(thresh1, (1024, 1024)))
        cv.imshow("Differenz Bild", cv.resize(img.astype('uint8'), (1024, 1024)))
        frame_counter = 0
    else:
        frame_counter += 1


if __name__ == '__main__':
    capture = VideoCapture()
    capture_thread = threading.Thread(target=capture.run)
    capture_thread.start()
    capture_thread.join()
    exit(0)
