from PySide6 import QtGui
from PySide6.QtCore import QObject

# from qtforms.Camera.camera_source import CameraSource
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QVideoSink, QCameraDevice, QMediaCaptureSession, QCameraDevice, QMediaPlayer, QCamera, QVideoFrame
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, pyqtSlot, pyqtSignal 
from PySide6.QtGui import QPixmap, QImage
import cv2, numpy as np
from camera_adapter import CameraAdapter

from camera_adapter import CameraAdapter, convert_qimage_qvideoframe
from .ui_CameraWidget import Ui_CameraWidget


class CameraWidget(QWidget):
    def __init__(self, camera_adapter:CameraAdapter=None, parent=None) -> None:
        super().__init__(parent)
        self.setup_ui()
        self.camera_adapter: CameraAdapter = None
        self.set_camera_source(camera_adapter)

    def setup_ui(self):
        self._ui = Ui_CameraWidget()
        self._ui.setupUi(self)

    def set_camera_source(self, camera_adapter:CameraAdapter):
        if camera_adapter is None:
            if self.camera_adapter is not None:
                del self.connection_error
                del self.connection_active_changed
            self._show_image_page()

            self.camera_adapter = None
        else:
            self._show_video_page()
        
            self.camera_adapter = camera_adapter
            self.camera_adapter.set_video_output(self._ui.video_widget)        
            self.connection_error = self.camera_adapter.camera.errorOccurred.connect(self._display_camera_error)
            self.connection_active_changed = self.camera_adapter.camera.activeChanged.connect(self._display_normal)
    
    def set_image_to_videowidget(self, qimage: QImage):
        frame = convert_qimage_qvideoframe(qimage)

        self._ui.video_widget.videoSink().setVideoFrame(frame)
        if self._ui.stackedWidget.currentIndex() != 0:
            self._show_video_page()

        # self._ui.image_label.setPixmap(QPixmap.fromImage(qimage))
        
        # if self._ui.stackedWidget.currentIndex() != 1:
        #     self._show_image_page()

    def set_image_to_label(self, qimage):
        pass

    def _show_video_page(self):
        self._ui.stackedWidget.setCurrentIndex(0)
    
    def _show_image_page(self):
        self._ui.stackedWidget.setCurrentIndex(1)
    
    @pyqtSlot()
    def _display_camera_error(self):
        if self.camera_adapter.camera.error() != QCamera.NoError:
            self._show_image_page()
        
    @pyqtSlot(bool)
    def _display_normal(self, camera_is_active):
        if camera_is_active:
            self._show_video_page()

    def closeEvent(self, a0) -> None:
        if self.camera_adapter is not None:
            self.camera_adapter.stop()
        return super().closeEvent(a0)