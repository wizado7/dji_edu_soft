from djitellopy import Tello #type:ignore
from PySide6.QtCore import QObject, Slot, Signal, QTimer, QThreadPool #type:ignore

from abstract_drone_controller import AbstractDroneController #type:ignore


class MockedDroneController(AbstractDroneController):
    def __init__(self,
                 forward_step=10,
                 backward_step=10,
                 yaw_step=30,
                 ) -> None:
        super().__init__()
        self._forward_step = forward_step
        self._backward_step = backward_step
        self._yaw_step = yaw_step
        self._is_connected = False
    
    @Slot()
    def _handle_client_changed(self):
        self.connected.emit()

    def start(self, ip:str, port:int):
        print(f'DRONE: START {ip}:{port}')
        self.moke_is_connected(True)
    
    def stop(self):
        self.moke_is_connected(False)
        print('DRONE: STOP')

    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    def moke_is_connected(self, is_connected):
        is_connected = bool(is_connected)
        if self._is_connected != is_connected:
            self._is_connected = is_connected
            if is_connected:
                self.connected.emit()
            else:
                self.disconnected.emit()

    def takeoff(self):
        print('DRONE: TAKEOFF')
    
    def land(self):
        print('DRONE: LAND')

    def move_fwd(self):
        print('DRONE: MOVE FORWARD')

    def move_bwd(self):
        print('DRONE: BACKWARD')

    def rotate_right(self):
        print('DRONE: ROTATE RIGHT')

    def rotate_left(self):
        print('DRONE: ROTATE LEFT')
    
    def stay(self):
        print('DRONE: STAY')
