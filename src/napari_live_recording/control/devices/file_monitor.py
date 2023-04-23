import cv2
import numpy as np
from dataclasses import replace
from napari_live_recording.common import ROI
from napari_live_recording.control.devices.interface import (
    ICamera,
    NumberParameter,
    ListParameter
)
from typing import Union, Any
from sys import platform

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tifffile import imread
from queue import LifoQueue

last_image_queue = LifoQueue(maxsize=1)

class FileMonitor(ICamera):

    class Handler(FileSystemEventHandler):
        @staticmethod
        def on_any_event(event):
            global last_image_queue
            if event.src_path.endswith('.tiff'):
                try:
                    last_image = imread(event.src_path)
                    if len(last_image) > 0:
                        last_image_queue.put(last_image)
                        # print(f"Yo! {event.src_path} 's shape is {last_image.shape}, {last_image.mean()}")
                except:
                    print("Unable to read file...")
            else:
                print("Unknown dispathch", event.src_path)

    def __init__(self, name: str, deviceID: Union[str, int]) -> None:
        """File Monitor wrapper.

        Args:
            name (str): user-defined camera/stream name.
            deviceID (Union[str, int]): path for monitored file(s).
        """

        # # initialize region of interest
        # # steps for height, width and offsets
        # # are by default 1. We leave them as such
        # sensorShape = ROI(offset_x=0, offset_y=0, height=9999, width=9999)
        
        parameters = {}
        path = deviceID

        self._observer = Observer()
        self._observer.schedule(self.Handler(), path, recursive=True)
        self._observer.start()

        # # exposure time in OpenCV is treated differently on Windows, 
        # # as exposure times may only have a finite set of values
        # if platform.startswith("win"):
        #     parameters["Exposure time"] = ListParameter(value=self.msExposure["15.6 ms"], 
        #                                                 options=list(self.msExposure.keys()), 
        #                                                 editable=True)
        # else:
        #     parameters["Exposure time"] = NumberParameter(value=10e-3,
        #                                                 valueLimits=(100e-6, 1),
        #                                                 unit="s",
        #                                                 editable=True)
        # parameters["Pixel format"] = ListParameter(value=self.pixelFormats["RGB"],
        #                                         options=list(self.pixelFormats.keys()),
        #                                         editable=True)

        # self.__format = self.pixelFormats["RGB"]
        super().__init__(name, deviceID, parameters, sensorShape=None)
    
    def setAcquisitionStatus(self, started: bool) -> None:
        pass
    
    def grabFrame(self) -> np.ndarray:
        # img = np.random.random(size=(500,500))
        while last_image_queue.empty():
            time.sleep(0.05)
        last_image = last_image_queue.get()
        print(f"image: {last_image.shape}, {last_image.dtype}, {last_image.mean()}")
        return last_image
    
    def changeParameter(self, name: str, value: Any) -> None:
        if name == "Exposure time":
            value = (self.msExposure[value] if platform.startswith("win") else value)
            self.__capture.set(cv2.CAP_PROP_EXPOSURE, value)
        elif name == "Pixel format":
            self.__format = self.pixelFormats[value]
        else:
            raise ValueError(f"Unrecognized value \"{value}\" for parameter \"{name}\"")
    
    def changeROI(self, newROI: ROI):
        if newROI <= self.fullShape:
            self.roiShape = newROI
    
    def close(self) -> None:
        print("Closing the file monitor...")
        self._observer.stop()
        self._observer.join()
        print("Done.")
