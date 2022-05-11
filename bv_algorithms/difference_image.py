import numpy as np


class DifferenceImage(object):

    def __init__(self, w: int, h: int):
        self.__reference_image = np.zeros(shape=(w, h), dtype=np.uint8)
        self.__reference_image_f = np.zeros(shape=(w, h), dtype=np.float64)
        self.__reference_image_set = False

    def save_reference_image(self, image: np.ndarray):
        self.__reference_image = image.copy()
        self.__reference_image_f = self.__reference_image_f.astype('float64')
        self.__reference_image_set = True
        return

    def clear_reference_image(self):
        self.__reference_image = np.zeros(shape=self.__reference_image.shape, dtype=np.uint8)
        self.__reference_image_f = np.zeros(shape=self.__reference_image.shape, dtype=np.float64)
        self.__reference_image_set = False
        return

    def apply(self, image: np.ndarray):
        if not self.__reference_image_set:
            raise Exception("Reference Image not set to generate difference image.")
        image_f = image.astype('float64')
        diff_img = np.where(abs(image_f - self.__reference_image) > 80, image_f, 0)
        return diff_img.astype('uint8')
