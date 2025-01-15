from enum import Enum
from PySide6.QtCore import QObject, Slot, Signal #type:ignore
from nm_client.pyside6.pyside6_nmclient import QNMClient, QConnectedClientInfo, RecievedMessage  #type:ignore
from nm_client.core.converters import bytes_to_int32  #type:ignore


class CommandsReader(QObject):
    command_stay = Signal()
    command_move_forward = Signal()
    command_move_backward = Signal()
    command_rotate_left = Signal()
    command_rotate_right = Signal()

    running_changed = Signal(bool)

    def __init__(self, nm_client:QNMClient) -> None:
        super().__init__()
        if not isinstance(nm_client, QNMClient):
            raise TypeError(f'Expected {QNMClient}, recieved {type(nm_client)}')
        
        self._client = nm_client
        self._client.recieved_msg.connect(self._handle_msg_recieved)
        self._client.is_connected_changed.connect(self._handle_is_connected_changed)
        self._code2command = {
            0: self.command_stay.emit,
            1: self.command_move_forward.emit,
            2: self.command_move_backward.emit,
            3: self.command_rotate_right.emit,
            4: self.command_rotate_left.emit
        }
    
    @property
    def running(self):
        return self._client.is_connected

    @Slot(bool)
    def _handle_is_connected_changed(self, is_connected):
        self.running_changed.emit(is_connected)

    @Slot(RecievedMessage)
    def _handle_msg_recieved(self, msg:RecievedMessage):
        payload = msg.payload
        # print(f'{payload=}')
        try:
            msg_code = bytes_to_int32(payload[:4])
            if msg_code != 17:
                return
            command_code = bytes_to_int32(payload[4:8])
            print(f'{command_code=}')
            if command_code not in self._code2command:
                return
            command = self._code2command[command_code]
            command()

        except Exception as e:
            import traceback
            print('Error at commands reading\n', traceback.format_tb(e.__traceback__), '\n', e)
