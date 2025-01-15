from pathlib import Path
from PySide6.QtCore import Slot, Signal, Qt

from abstract_drone_controller import AbstractDroneController
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget,
QApplication, QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox)


class DroneKBControllWidget(QWidget):
    def __init__(self, drone_controller:AbstractDroneController):
        super().__init__()
        self.drone_controller = drone_controller

        src_dir = Path(__file__).parent / 'src'

        self._move_fwd_btn = QPushButton(QIcon(str(src_dir / 'up-arrow.png')), 'Вперёд')
        self._move_bwd_btn = QPushButton(QIcon(str(src_dir / 'down-arrow.png')), 'Назад')
        self._stay_btn = QPushButton(QIcon(str(src_dir / 'stop-button.png')), 'Стоять')
        self._rotate_left_btn = QPushButton(QIcon(str(src_dir / 'rotate-left.png')), 'Влево')
        self._rotate_right_btn = QPushButton(QIcon(str(src_dir / 'rotate-right.png')), 'Вправо')

        self._move_up_btn = QPushButton('Вверх')
        self._move_down_btn = QPushButton('Вниз')

        self._takeoff_btn = QPushButton(QIcon(str(src_dir / 'takeoff.png')), 'Взлёт')
        self._landing_btn = QPushButton(QIcon(str(src_dir / 'landing.png')), 'Посадка')

        self._move_fwd_btn.clicked.connect(self._fwd_clicked)
        self._move_bwd_btn.clicked.connect(self._bwd_clicked)
        self._takeoff_btn.clicked.connect(self._takeoff_clicked)
        self._landing_btn.clicked.connect(self._land_clicked)
        self._rotate_left_btn.clicked.connect(self._rotate_left_clicked)
        self._rotate_right_btn.clicked.connect(self._rotate_right_clicked)
        self._stay_btn.clicked.connect(self._stay_clicked)

        self._move_up_btn.clicked.connect(self._up_clicked)
        self._move_down_btn.clicked.connect(self._down_clicked)

        grid = QGridLayout()

        grid.addWidget(self._takeoff_btn, 0, 0)
        grid.addWidget(self._landing_btn, 0, 2)

        grid.addWidget(self._move_fwd_btn, 0, 1)
        grid.addWidget(self._rotate_left_btn, 1, 0)
        grid.addWidget(self._stay_btn, 1, 1)
        grid.addWidget(self._rotate_right_btn, 1, 2)
        grid.addWidget(self._move_bwd_btn, 2, 1)
        grid.addWidget(self._move_up_btn, 2, 0)
        grid.addWidget(self._move_down_btn, 2, 2)
        self.setLayout(grid)

    @Slot()
    def _up_clicked(self):
        self.drone_controller.up()

    @Slot()
    def _down_clicked(self):
        self.drone_controller.down()

    @Slot()
    def _fwd_clicked(self):
        self.drone_controller.move_fwd()

    @Slot()
    def _bwd_clicked(self):
        self.drone_controller.move_bwd()

    @Slot()
    def _takeoff_clicked(self):
        self.drone_controller.takeoff()
    
    @Slot()
    def _land_clicked(self):
        self.drone_controller.land()
    
    @Slot()
    def _rotate_left_clicked(self):
        self.drone_controller.rotate_left()
    
    @Slot()
    def _rotate_right_clicked(self):
        self.drone_controller.rotate_right()

    @Slot()
    def _stay_clicked(self):
        self.drone_controller.stay()
