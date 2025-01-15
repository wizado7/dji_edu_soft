import sys
from threading import Thread

from PySide6.QtCore import Slot, QTimer
import traceback
from PySide6.QtWidgets import (QWidget,
QApplication, QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox)
from nm_client.pyside6.gui.qt_control import QNMClientControl, QNMClient #type:ignore

from commands_reader import CommandsReader
from dron_kb_controll import DroneKBControllWidget
from drone_connect_disconnect_widget import DroneConnectDisconnectWidget
from drone_controller import DroneController
from drone_controller2 import DroneController2
from mocked_drone_controller import MockedDroneController
from dron_config import DroneConfig
import os, logging
import datetime
import cv2
import djitellopy as Tello


logs_folder = "logs"
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)
# video_folder = "videos"
# if not os.path.exists(video_folder):
#     os.makedirs(video_folder)

# Проверка наличия папки с логами и создание, если она не существует
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)

# Создание имени файла лога на основе текущей даты и времени
log_file_name = f"keyboard_input_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

# Создание пути к файлу лога
log_file_path = os.path.join(logs_folder, log_file_name)

# Инициализация логгера
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

frame_buffer = []



class DroneControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Управление DJI дроном')
        # logic
        self._nm_client = QNMClient()
        self._drone_config = DroneConfig()

        # self._drone_controller = MockedDroneController()
        self._drone_controller = DroneController()
        # self._drone_controller = DroneController2(do_cam_read=True)
        self._drone_controller.drone_error.connect(self._handle_drone_error)
        self._drone_controller.camera_frame_changed.connect(self._handle_camera_frame_changed)

        self._commands_reader = CommandsReader(self._nm_client)
        self._commands_reader.command_move_forward.connect(self._drone_controller.move_fwd)
        self._commands_reader.command_move_backward.connect(self._drone_controller.move_bwd)
        self._commands_reader.command_rotate_left.connect(self._drone_controller.rotate_left)
        self._commands_reader.command_rotate_right.connect(self._drone_controller.rotate_right)
        self._commands_reader.command_stay.connect(self._drone_controller.stay)

        # gui
        self._nm_client_controll = QNMClientControl(client=self._nm_client)
        self._drone_kb_controll = DroneKBControllWidget(self._drone_controller)

        self._drone_connect_disconnect_widget = DroneConnectDisconnectWidget(self._drone_controller, self._drone_config)

        vbox = QVBoxLayout()
        vbox.addWidget(self._nm_client_controll)
        vbox.addWidget(self._drone_connect_disconnect_widget)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self._drone_kb_controll)
        
        w = QWidget()
        w.setLayout(hbox)
        self.setCentralWidget(w)

    @Slot(tuple)
    def _handle_drone_error(self, err_data):
        print('Registered drone error:', err_data)

    def closeEvent(self, ev):
        self._nm_client.disconnect_client()

    # VS_UDP_IP = '0.0.0.0'
    #
    # # Video stream, server socket
    # VS_UDP_PORT = 11111
    # def get_udp_video_address(self):
    #     return 'udp://@' + self.VS_UDP_IP + ':' + str(self.VS_UDP_PORT)  # + '?overrun_nonfatal=1&fifo_size=5000'

    # cap = None

    # VideoCapture object
    # background_frame_read = None
    # def get_frame_read(self):
    #     """Get the BackgroundFrameRead object from the camera drone. Then, you just need to call
    #     backgroundFrameRead.frame to get the actual frame received by the drone.
    #     Returns:
    #         BackgroundFrameRead
    #     """
    #     if self.background_frame_read is None:
    #         self.background_frame_read = BackgroundFrameRead(self, self.get_udp_video_address()).start()
    #     return self.background_frame_read

    @Slot()
    def _handle_camera_frame_changed(self):
        img = self._drone_controller.frame
        # img = self.get_frame_read().frame
        if img is not None:
            print("Camera frame changed")
            img = cv2.resize(img, (640, 480))
            cv2.imshow('dron cam', img)


class BackgroundFrameRead:
    """
    This class read frames from a VideoCapture in background. Then, just call backgroundFrameRead.frame to get the
    actual one.
    """

    def __init__(self, tello, address):
        tello.cap = cv2.VideoCapture(address)
        self.cap = tello.cap

        if not self.cap.isOpened():
            self.cap.open(address)

        self.grabbed, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update_frame, args=()).start()
        return self

    def update_frame(self):
        while not self.stopped:
            if not self.grabbed or not self.cap.isOpened():
                self.stop()
            else:
                (self.grabbed, self.frame) = self.cap.read()

    def stop(self):
        self.stopped = True

# Override the excepthook
def exception_hook(exc_type, exc_value, exc_traceback):
    print(f"Uncaught exception:", exc_value, file=sys.stderr)
    print(traceback.format_exc())
    
    QTimer.singleShot(0, app.quit)
    sys._excepthook(exc_type, exc_value, exc_traceback)  # Call the original excepthook #type:ignore
    raise exc_value

sys._excepthook = sys.excepthook  # Backup the original excepthook #type:ignore
sys.excepthook = exception_hook  # Set the custom excepthook


if __name__ == '__main__':
    app = QApplication(sys.argv)
    drone_control_app = DroneControlApp()
    drone_control_app.show()
    app.exec()