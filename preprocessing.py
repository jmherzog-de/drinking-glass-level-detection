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
    cv.imshow("Live Image", cv.resize(image_8bit, (1024, 1024)))

    blur = cv.blur(image_8bit, (3, 3))
    cv.imwrite("sample.png", blur)
    exit(0)
    cv.waitKey(1)


if __name__ == '__main__':
    capture = VideoCapture(frame_available_callback=update_original_frame)
    capture_thread = threading.Thread(target=capture.run)
    capture_thread.start()
    capture_thread.join()
    exit(0)
