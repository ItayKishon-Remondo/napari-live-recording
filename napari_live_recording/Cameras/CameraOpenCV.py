from .ICamera import CameraROI, ICamera
from platform import system
import cv2
import numpy as np

CAM_OPENCV = "Default Camera (OpenCV)"

class CameraOpenCV(ICamera):
    """Generic OpenCV camera handler
    """

    def __init__(self) -> None:
        super().__init__()
        self.camera_idx = 0
        self.camera_api = cv2.CAP_ANY
        self.camera = None
        self.camera_name = CAM_OPENCV
        self.width = self.full_width = 0
        self.height = self.full_height = 0
        self.roi = CameraROI()

        # Windows platforms support discrete exposure times
        # These are mapped using a dictionary
        # todo: add support for Linux
        self.exposure_dict = {
            "1 s":  0,
            "500 ms": -1,
            "250 ms": -2,
            "125 ms": -3,
            "62.5 ms": -4,
            "31.3 ms": -5,
            "15.6 ms": -6,
            "7.8 ms": -7,
            "3.9 ms": -8,
            "2 ms": -9,
            "976.6 us": -10,
            "488.3 us": -11,
            "244.1 us": -12,
            "122.1 us": -13
        }

        self.frame_counter = 0

    def __del__(self) -> None:
        if self.camera is not None:
            self.camera.release()

    def __str__(self) -> str:
        return CAM_OPENCV

    def open_device(self) -> bool:
        ret = False

        if self.camera is None:
            self.camera = cv2.VideoCapture(self.camera_idx, self.camera_api)
            ret = self.camera.isOpened()
        else:
            ret = self.camera.open(self.camera_idx, self.camera_api)

        self.full_width = self.width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.full_height = self.height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

        return ret

    def close_device(self) -> None:
        self.camera.release()

    def get_available_pixel_formats(self) -> list:
        return ["No pixel format available"]

    def set_pixel_format(self, format) -> None:
        pass

    def capture_image(self) -> np.array:
        _, img = self.camera.read()
        y, h = self.roi.offset_y, self.roi.offset_y + self.roi.height
        x, w = self.roi.offset_x, self.roi.offset_x + self.roi.width
        img = img[y:h, x:w]        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.frame_counter += 1
        return img

    def set_exposure(self, exposure) -> None:
        if system() == "Windows":
            exposure = self.exposure_dict[exposure]
        self.camera.set(cv2.CAP_PROP_EXPOSURE, exposure)

    def set_roi(self, roi: CameraROI) -> None:
        self.roi = roi

    def get_roi(self) -> CameraROI:
        return self.roi

    def set_full_frame(self) -> None:
        self.width = self.full_width
        self.height = self.full_height
        self.roi = CameraROI(width = self.full_width,
                            height = self.full_height)
    
    def get_sensor_range(self) -> CameraROI:
        return CameraROI(width = self.full_width,
                        height = self.full_height)

    def get_acquisition(self) -> bool:
        return self.camera.isOpened()

    def set_acquisition(self, is_enabled) -> None:
        if is_enabled:
            if self.camera is None:
                self.camera = cv2.VideoCapture(self.camera_idx, self.camera_api)
            else:
                self.camera.open(self.camera_idx, self.camera_api)
        else:
            self.camera.release()

    def get_frames_per_second(self) -> int:
        frames = self.frame_counter
        self.frame_counter = 0
        return frames
