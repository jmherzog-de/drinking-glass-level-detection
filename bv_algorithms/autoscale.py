import ctypes
import platform
import numpy as np
import os

if platform.system() == 'Windows':
    lib = ctypes.CDLL(os.path.dirname(os.path.realpath(__file__)) + "\\bv_algorithms_cpp.dll")
elif platform.system() == 'Darwin':
    lib = ctypes.CDLL(os.path.dirname(os.path.realpath(__file__)) + "/libbv_algorithms_cpp.dylib")
else:
    raise Exception(f"No implementations for this System: {platform.system()}")

c_int_array = np.ctypeslib.ndpointer(dtype=np.uint16, ndim=2, flags=['C_CONTIGUOUS', 'WRITEABLE'])
BV_HelperHandle = ctypes.POINTER(ctypes.c_char)
lib.createInstance.argtypes = []
lib.createInstance.restype = BV_HelperHandle
lib.createLookUpTable.argtypes = [BV_HelperHandle, ctypes.c_uint16, ctypes.c_uint16]
lib.apply.argtypes = [BV_HelperHandle, c_int_array]


class AutoscaleImage(object):
    """
    Binding class to C++ autoscaling methods.

    This class contains binding to generate a Look-Up table and create an auto-scaled image.
    Note: Works with 16-bit image.
    """

    def __init__(self):
        self.instance = lib.createInstance()

    def create_lookup_table(self, t_min: int, t_max: int) -> None:
        """
        Create Look-Up table with min and max pixel value.
        :param t_min: Minimum pixel value.
        :param t_max: Maximum pixel value.
        :return: None
        """
        lib.createLookUpTable(self.instance, t_min, t_max)

    def autoscale(self, image: np.ndarray):
        """
        Perform autoscaling for any input image.
        :param image: Input grayscale 16-bit image
        :return: Scaled 16-bit image.
        """
        scaled_image = image.copy()
        lib.createLookUpTable(self.instance, image.min(), 32750)
        lib.apply(self.instance, scaled_image)
        return scaled_image
