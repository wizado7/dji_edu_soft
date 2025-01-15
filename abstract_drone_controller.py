from djitellopy import Tello #type:ignore
from PySide6.QtCore import QObject, Slot, Signal, QTimer, QThreadPool #type:ignore
from time import time
from nm_client.pyside6.worker import Worker #type:ignore
import numpy as np


class AbstractDroneController(QObject):
    drone_error = Signal(tuple) # exctype, value, traceback.format_exc()

    connected = Signal()
    disconnected = Signal()

    camera_frame_changed = Signal()
    camera_started = Signal()
    camera_stopped = Signal()
    camera_error = Signal(tuple) 

    client_changed = Signal()

    def __init__(self,
                 forward_step=20,
                 backward_step=20,
                 yaw_step=30,
                 do_cam_read=False
                 ) -> None:
        super().__init__()
        self._forward_step = forward_step
        self._backward_step = backward_step
        self._yaw_step = yaw_step
        self._do_cam_read = do_cam_read
        self.drone_error.connect(self.stop)
    
    # def set_tello_client(self, client:Tello|None):
    #     if client is not None and not isinstance(client, Tello):
    #         raise TypeError(f'Expected {Tello}, recieved {type(client)}')
    #     self._tello_client = client

    def start(self, ip:str, port:int) -> None:
        raise NotImplementedError()
    
    def stop(self):
        raise NotImplementedError()
    
    @property
    def do_cam_read(self):
        return self._do_cam_read

    @do_cam_read.setter
    def do_cam_read(self, do_read:bool):
        do_read = bool(do_read)
        if self._do_cam_read != do_read:
            self._do_cam_read = do_read
    
    @property
    def frame(self)->np.ndarray|None:
        return None

    @property
    def is_connected(self) -> bool:
        raise NotImplementedError()

    def takeoff(self):
        raise NotImplementedError()
    
    def land(self):
        raise NotImplementedError()

    def up(self):
        pass

    def down(self):
        pass

    def move_fwd(self):
       raise NotImplementedError()

    def move_bwd(self):
        raise NotImplementedError()

    def rotate_right(self):
        raise NotImplementedError()

    def rotate_left(self):
        raise NotImplementedError()
    
    def stay(self):
        raise NotImplementedError()
