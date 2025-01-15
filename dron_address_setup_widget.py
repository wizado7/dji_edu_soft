from pathlib import Path
from PySide6.QtCore import Slot, Signal, Qt

from abstract_drone_controller import AbstractDroneController
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget,
QApplication, QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox)


class DroneAddressSetupWidget(QWidget):
    host_submitted = Signal(str, int)

    def __init__(self, current_ip:str, current_port:int):
        super().__init__()
        self.setWindowTitle('Выбор адреса подключения дрона')
        grid = QGridLayout()
        self._ip_input = QLineEdit(str(current_ip))
        self._port_input = QSpinBox()
        self._port_input.setMaximum(64000)
        self._port_input.setMinimum(1000)
        self._port_input.setValue(current_port)
        grid.addWidget(QLabel('Ip:'), 0, 0)
        grid.addWidget(self._ip_input, 0, 1)
        grid.addWidget(QLabel('Port:'), 1, 0)
        grid.addWidget(self._port_input, 1, 1)
        
        vbox = QVBoxLayout()
        self._submit_btn = QPushButton('Подтвердить')
        self._submit_btn.clicked.connect(self._handle_submit_clicked)
        
        vbox.addLayout(grid)
        vbox.addWidget(self._submit_btn)
        
        self.setLayout(vbox)

        # self.setWindowModality(Qt.WindowModality.NonModal)
    
    @Slot()
    def _handle_submit_clicked(self):
        self.host_submitted.emit(self.ip, self.port)
        self.hide()

    @property
    def ip(self):
        return self._ip_input.text()
    
    @ip.setter
    def ip(self, val:str):
        self._ip_input.setText(val)

    @property
    def port(self):
        return self._port_input.value()
    
    @port.setter
    def port(self, val:int):
        self._port_input.setValue(int(val))
