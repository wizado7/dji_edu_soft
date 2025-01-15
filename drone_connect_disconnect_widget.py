from pathlib import Path
from typing import cast
from PySide6.QtCore import Slot, Signal, Qt
from djitellopy import Tello

from abstract_drone_controller import AbstractDroneController
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget,
QApplication, QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox, QLabel, QLineEdit, QSpinBox)
from nm_client.pyside6.gui.qt_control import QNMClientControl, QNMClient #type:ignore

from commands_reader import CommandsReader
from dron_address_setup_widget import DroneAddressSetupWidget
from dron_kb_controll import DroneKBControllWidget
from mocked_drone_controller import MockedDroneController
from dron_config import DroneConfig


class DroneConnectDisconnectWidget(QWidget):
    def __init__(self, 
                 drone_controller:AbstractDroneController,
                 drone_config:DroneConfig):
        super().__init__()
        self._drone_controller = drone_controller
        
        self._drone_config = drone_config

        self._drone_connect_btn = QPushButton('Подключить')
        self._drone_disconnect_btn = QPushButton('Отключить')

        self._host_select_dialog = DroneAddressSetupWidget(self._drone_config.ip, self._drone_config.port)
        self._host_select_dialog.host_submitted.connect(self._handle_host_submitted)

        self._select_host_btn = QPushButton('Выбрать адрес дрона')
        self._select_host_btn.clicked.connect(self._handle_select_host_clicked)
        self._selected_host_input = QLineEdit(f'{self._drone_config.ip}:{self._drone_config.port}')
        self._selected_host_input.setReadOnly(True)

        self._drone_connect_btn.clicked.connect(self._drone_connect_clicked)
        self._drone_disconnect_btn.clicked.connect(self._drone_disconnect_clicked)

        self._set_is_connected(self._drone_controller.is_connected)
        self._drone_controller.connected.connect(self._handle_drone_connected)
        self._drone_controller.disconnected.connect(self._handle_drone_disconnected)


        vbox = QVBoxLayout()
        vbox.addWidget(self._drone_connect_btn)
        vbox.addWidget(self._drone_disconnect_btn)
        vbox.addWidget(self._select_host_btn)
        vbox.addWidget(self._selected_host_input)
        
        self.setLayout(vbox)

    @Slot()
    def _handle_drone_connected(self):
        self._set_is_connected(True)

    @Slot()
    def _handle_drone_disconnected(self):
        self._set_is_connected(False)

    @Slot()
    def _handle_select_host_clicked(self):
        self._host_select_dialog.show()

    @Slot(str, int)
    def _handle_host_submitted(self, ip:str, port:int):
        self._drone_config.ip = ip
        self._drone_config.port = port
        self._selected_host_input.setText(f'{self._drone_config.ip}:{self._drone_config.port}')

    @Slot()
    def _drone_connect_clicked(self):
        if self._drone_controller.is_connected:
            return
        
        self._drone_controller.start(self._drone_config.ip, self._drone_config.port)

    @Slot()
    def _drone_disconnect_clicked(self):
        if not self._drone_controller.is_connected:
            return
        
        self._drone_controller.stop()

    @Slot(bool)
    def _handle_is_connected_changed(self, is_connected:bool):
        self._set_is_connected(is_connected)
    
    def _set_is_connected(self, is_connected:bool):
        if is_connected:
            if not self._host_select_dialog.isHidden():
                self._host_select_dialog.hide()
        else:
            self._host_select_dialog.show()

        self._select_host_btn.setEnabled(not is_connected)
        
        self._drone_connect_btn.setEnabled(not is_connected)
        self._drone_disconnect_btn.setEnabled(is_connected)
        # self.closeEvent()

    def closeEvent(self, ev):
        self._host_select_dialog.close()
