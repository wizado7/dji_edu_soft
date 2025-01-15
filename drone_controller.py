from PySide6.QtCore import QObject, Slot, Signal, QTimer, QThreadPool #type:ignore
from time import time, sleep
from nm_client.pyside6.worker import Worker #type:ignore
from djitellopy import Tello  #type:ignore
from abstract_drone_controller import AbstractDroneController
import numpy as np


class DroneController(AbstractDroneController):
    def __init__(self,
                 forward_step=40,
                 backward_step=40,
                 yaw_step=90,
                 update_timeout=10,
                 do_cam_read=False
                 ) -> None:
        super().__init__(forward_step=forward_step,
                         backward_step=backward_step,
                         yaw_step=yaw_step,
                         do_cam_read=do_cam_read)
        self._update_timeout = update_timeout
        self._tello_client:Tello|None = None

        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._update_dron_check_timeout)
        self.timer.start()

        self.__executing_worker = False

        self.threadpool = QThreadPool()
        self._is_connected = False
        self._last_frame:np.ndarray|None = None

    @Slot()
    def _update_dron_check_timeout(self):
        if self._tello_client is None:
            return
        now = time()*1000
        if now - self._tello_client.last_received_command > self._update_timeout*1000:
            print('SEND KEEP ALIVE')
            self._tello_client.send_rc_control(0, 0, 0, 0)
            # self._tello_client.send_command_without_return('keepalive')

    def __run_drone_command_worker(self, worker:Worker):
        if self.__executing_worker:
            return
        worker.signals.error.connect(self._handle_drone_error)
        worker.signals.finished.connect(self._handle_command_worker_finished)
        self.threadpool.start(worker)

    @Slot()
    def _handle_command_worker_finished(self):
        self.__executing_worker = False

    @Slot(tuple)
    def _handle_drone_error(self, error_data:tuple):
        self.drone_error.emit(error_data)

    def start(self, ip:str, port:int):
        if self._tello_client is not None:
            return
        
        def start_tello_drone(self=self, ip=ip, port=port):
            print('start tello'+ f'{ip}:{port}')
            # tello = Tello(f'{ip}:{port}')
            tello = Tello(ip, port)

            print('start ok')
            tello.connect()
            # print('DRONE BATTERY', tello.get_battery())
            self._tello_client = tello
            print('befora cam worker created')
            cam_worker = Worker(self.__streamon_blocking)
            self.threadpool.start(cam_worker)

        worker = Worker(start_tello_drone)
        worker.signals.result.connect(self._handle_dron_connected)
        self.__run_drone_command_worker(worker)

    @Slot()
    def _handle_dron_connected(self):
        self.__update_is_connected(True)

    def stop(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.end)
        worker.signals.result.connect(self._handle_dron_disconnected)
        self.__run_drone_command_worker(worker)

    # def streamon(self):
    #     pass
    
    def __streamon_blocking(self):
        if self._tello_client is None:
            print(f'{self._tello_client=}')
            return
        if self._tello_client.stream_on:
            print(f'{self._tello_client.stream_on=}')
            return
        try:
            self._tello_client.streamon()
            # self.camera_started.emit()
            cap = self._tello_client.get_video_capture()
            
            print(f'{cap.isOpened()=}')
            while cap.isOpened() and self.is_connected:
                # Capture frame-by-frame
                ret, frame = cap.read() 
                # print(f'{cap.isOpened()=}, {frame[:100]}')
                if ret:
                    self._last_frame = frame
                    self.camera_frame_changed.emit()
                else:
                    break
                # Display the resulting frame 
                    # cv2.imshow('Frame', frame) 
        except Exception as e:
            print(e)
            import traceback
            self.camera_error.emit((type(e), e, traceback.format_tb(e.__traceback__)))
        finally:
            self.camera_stopped.emit()
        # frames_reader_worker = Worker(read_cam_frames)
        # self.threadpool.start(frames_reader_worker)

    @Slot()
    def _handle_dron_disconnected(self):
        self.__update_is_connected(False)

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def __update_is_connected(self, val:bool):
        val = bool(val)
        if val != self._is_connected:
            self._is_connected = val
            if self._is_connected:
                self.connected.emit()
            else:
                self.disconnected.emit()
    
    @property
    def frame(self):
        return self._last_frame

    def takeoff(self):
        if self._tello_client is None:
            return
        
        worker = Worker(self._tello_client.takeoff)
        self.__run_drone_command_worker(worker)

    def up(self):
        if self._tello_client is None:
            return

        worker = Worker(self._tello_client.move_up, 20)
        self.__run_drone_command_worker(worker)

    def down(self):
        if self._tello_client is None:
            return

        worker = Worker(self._tello_client.move_down, 20)
        self.__run_drone_command_worker(worker)
    
    def land(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.land)
        self.__run_drone_command_worker(worker)

    def move_fwd(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.move_forward, self._forward_step)
        self.__run_drone_command_worker(worker)

    def move_bwd(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.move_back, self._backward_step)
        self.__run_drone_command_worker(worker)

    def rotate_right(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.rotate_clockwise, self._yaw_step)
        self.__run_drone_command_worker(worker)

    def rotate_left(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.rotate_counter_clockwise, self._yaw_step)
        self.__run_drone_command_worker(worker)
    
    def stay(self):
        if self._tello_client is None:
            return
        # worker = Worker(self._tello_client.set_speed, 0)
        # self.__run_drone_command_worker(worker)
