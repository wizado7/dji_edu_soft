from PySide6.QtCore import QObject, Slot, Signal, QTimer, QThreadPool #type:ignore
from time import time, sleep
from nm_client.pyside6.worker import Worker #type:ignore
from abstract_drone_controller import AbstractDroneController
import numpy as np
from tellopy import Tello
import cv2, av


class DroneController2(AbstractDroneController):
    def __init__(self,
                 forward_step=100,
                 backward_step=100,
                 yaw_step=100,
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
        self.timer.setInterval(250)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._update_dron_check_timeout)
        self.timer.start()

        self.__executing_worker = False

        self.threadpool = QThreadPool()
        self._is_connected = False
        self._last_frame:np.ndarray|None = None

        self._last_command = time()

        self._exponential_smoothing_timer = QTimer()
        self._exponential_smoothing_timer.setInterval(80)
        self._exponential_smoothing_timer.setSingleShot(False)
        self._exponential_smoothing_timer.timeout.connect(self._handle_exponential_smoothing)
        self._exponential_smoothing_timer.start()

    @Slot()
    def _handle_exponential_smoothing(self):
        client = self._tello_client
        # print(f'{client=}')
        if client is None:
            return
        def scale_and_threshold(val, scale=0.8, min_clamp=1/100*0.5):
            val = val*scale
            if abs(val) < min_clamp:
                return 0
            return val
        
        client.left_x, client.left_y, client.right_x, client.right_y = (
            scale_and_threshold(client.left_x), 
            scale_and_threshold(client.left_y), 
            scale_and_threshold(client.right_x),
            scale_and_threshold(client.right_y))
        # print(f'{(client.left_x, client.left_y, client.right_x, client.right_y)}')

    @Slot()
    def _update_dron_check_timeout(self):
        if self._tello_client is None:
            return
        now = time()
        if now - self._last_command > self._update_timeout:
            self._tello_client.down(0)
            self.__update_last_command()
            # self._tello_client.send_command_without_return('keepalive')

    def __run_drone_command_worker(self, worker:Worker):
        if self.__executing_worker:
            return
        worker.signals.error.connect(self._handle_drone_error)
        worker.signals.finished.connect(self._handle_command_worker_finished)
        self.threadpool.start(worker)
        self.__update_last_command()

    def __update_last_command(self):
        self._last_command = time()

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
            tello = Tello()

            print('start ok')
            tello.connect()
            

            self._tello_client = tello
            self.__update_last_command()

            # if self._do_cam_read:
            #     video_worker = Worker(self.__streamon_blocking)
            #     self.threadpool.start(video_worker)

        worker = Worker(start_tello_drone)
        worker.signals.result.connect(self._handle_dron_connected)
        self.__run_drone_command_worker(worker)

    @Slot()
    def _handle_dron_connected(self):
        self.__update_is_connected(True)

    def stop(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.quit)
        worker.signals.result.connect(self._handle_dron_disconnected)
        self.__run_drone_command_worker(worker)

    # def streamon(self):
    #     pass
    
    def __streamon_blocking(self):
        if self._tello_client is None:
            return
        try:
            container = av.open(self._tello_client.get_video_stream())
        # skip first 300 frames
            frame_skip = 300
            while True:
                for frame in container.decode(video=0):
                    # if 0 < frame_skip:
                    #     frame_skip = frame_skip - 1
                    #     continue
                    start_time = time.time()
                    print(frame)
                    # image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                    # self._last_frame = image
                    # self.camera_frame_changed.emit()
        except Exception as e:
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
    
    def land(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.land)
        self.__run_drone_command_worker(worker)

    def move_fwd(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.forward, self._forward_step)
        self.__run_drone_command_worker(worker)

    def move_bwd(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.backward, self._backward_step)
        self.__run_drone_command_worker(worker)

    def rotate_right(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.set_yaw, self._yaw_step/100)
        self.__run_drone_command_worker(worker)

    def rotate_left(self):
        if self._tello_client is None:
            return
        worker = Worker(self._tello_client.set_yaw, -self._yaw_step/100)
        self.__run_drone_command_worker(worker)
    
    def stay(self):
        if self._tello_client is None:
            return
        # worker = Worker(self._tello_client.set_speed, 0)
        # self.__run_drone_command_worker(worker)
