"""SCTSocket Referenz
"""

import socket
import json
import time
from enum import IntEnum
from struct import Struct
from typing import Any


def create_socket(url: str, port: int, client: bool = True):
    """Helper function to create a new socket connection
        Arguments:
            - url (str): url to connect/listen to
            - port (int): port to connect/listen to
            - client (bool): If False return a listener
        Returns:
            - socket.socket
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if client:
        for _ in range(50): #10 sek retry
            try:
                sock.connect((url, port))
                return sock
            except:
                time.sleep(0.2)
        raise ConnectionError("Couldn't connect to socket...")
    sock.bind((url, port))
    sock.listen()
    return sock


class PacketType(IntEnum):
    none = -1
    init = 1
    debug = 2
    data = 3


class PayloadType(IntEnum):
    plain = 0
    binary = 1
    JSON = 2


class Packet:
    def __init__(
        self,
        packet_type=PacketType.none,
        payload: Any = "",
        payload_type: PayloadType = PayloadType.plain,
    ):
        self.payload = payload
        self.payload_type = payload_type
        self.packet_type = packet_type


class _Packet:
    HEADER = Struct("<iii")

    def __init__(self, packet_type: PacketType = PacketType.none, payload: Any = ""):
        self.packet_type = packet_type
        self.payload_type = PayloadType.binary
        if isinstance(payload, str):
            self.payload_type = PayloadType.plain
        elif not isinstance(payload, bytes):
            self.payload_type = PayloadType.JSON
            payload = json.dumps(payload)
        if isinstance(payload, str):
            payload = payload.encode("utf8")
        self.payload: bytes = payload
        self.size = len(self.payload)

    def get(self) -> Packet:
        return Packet(self.packet_type, self.get_payload(), self.payload_type)

    def get_payload(self) -> Any:
        if self.payload_type == PayloadType.binary:
            return self.payload
        payload = self.payload.decode("utf8")
        if self.payload_type == PayloadType.JSON:
            payload = json.loads(payload)
        return payload

    def get_header(self) -> bytes:
        return self.HEADER.pack(self.packet_type, self.size, self.payload_type)

    def set_header(self, data: bytes):
        (t, s, pt) = self.HEADER.unpack(data)
        self.packet_type = PacketType(t)
        self.size = s
        self.payload_type = pt
        return s

    def __str__(self):
        return f"{self.__class__}: {self.packet_type!r} {self.payload_type!r}, {self.get_payload()}"


class SCTSock:
    def __init__(self, sock: socket.socket, close=True, *, timeout=30):
        sock.settimeout(timeout)
        self._sock = sock
        self._open = True
        self._close = close

    def __del__(self):
        if not self._close:
            return
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, e, msg, tb):
        self.__del__()
        if e:
            raise

    def close(self):
        """Close connection"""
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
        except Exception:
            pass
        self._open = False

    def send_init(self, payload: Any = ""):
        """Send init Packet

            Arguments:
                - payload (Any): Can be any JSON Serializable type, str or bytes
            Returns:
                - Success (boolean)
        """
        return self._send(_Packet(PacketType.init, payload))

    def send_debug(self, payload: Any = ""):
        """Send debug Packet

            Arguments:
                - payload (Any): Can be any JSON Serializable type, str or bytes
            Returns:
                - Success (boolean)
        """
        return self._send(_Packet(PacketType.debug, payload))

    def send_data(self, payload: Any = ""):
        """Send data Packet

            Arguments:
                - payload (Any): Can be any JSON Serializable type, str or bytes
            Returns:
                - Success (boolean)
        """
        return self._send(_Packet(PacketType.data, payload))

    def _send(self, data: _Packet) -> bool:
        """Sends the given packet.

            Notes:
                - Closes connection if an error occurs.
            Returns:
                - Success (boolean)
        """
        if not self._open:
            return False
        try:
            self._sock.sendall(data.get_header())
            if len(data.payload) > 0:
                self._sock.sendall(data.payload)
        except OSError:
            self._open = False
            return False
        return True

    def _recv(self, length: int):
        data = b""
        if length <= 0:
            return data
        while length > len(data):
            _data = self._sock.recv(length - len(data))
            if len(_data) == 0:
                self.open = False
                raise IOError("Socket is closed!")
            data = data + _data
        return data

    def recv(self) -> Packet:
        """Receives Packet:

            Returns:
                - Packet

            Notes:
                - return Packet with PacketType none if no packet was received or the connection is closed
        """
        if not self._open:
            return Packet()
        p = _Packet()
        try:
            data = self._recv(p.HEADER.size)
            p.set_header(data)
            data = self._recv(p.size)
            p.payload = data
        except IOError:
            return Packet()
        return p.get()
