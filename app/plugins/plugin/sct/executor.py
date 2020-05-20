from django.conf import settings as django_settings

from ...exception import PluginException
from ..executor import Executor as BaseExecutor

from app.util import log as logging
from app.util.sctsock import SCTSock, create_socket, PacketType


class Executor(BaseExecutor):
    """ This Executor manages TCP connections with the SCT protocol.
        you need to implement get_url and get_port.

        you need to call 'execute' at the top of your execute Method.
    """
    def __init__(self, *args, **kwargs):
        with logging.LogCall(__file__, "__init__", self.__class__):
            super().__init__(*args, **kwargs)
            self._sct_debug = []
            self._sct_data = None

    def get_url(self) -> str:
        # implement this
        return ""

    def get_port(self) -> int:
        # implement this
        return 0

    def get_request(self) -> dict:
        data = {"code": self.request.code, "test": self.request.test}
        return data

    def get_settings(self) -> dict:
        return self.request.settings

    def sct_get_data(self):
        return self._sct_data

    def sct_get_debug(self) -> list:
        return self._sct_debug

    def execute(self):
        with logging.LogCall(__file__, "execute", self.__class__):
            self._sct_send()


    def _sct_loop(self, sock):
        packet = sock.recv()  # blocking....
        payload = packet.payload
        if packet.packet_type == PacketType.init:
            if payload == "init":
                sock.send_init(self.get_settings())
            elif payload == "data":
                sock.send_init(self.get_request())
            return True
        elif packet.packet_type == PacketType.debug:
            self._sct_debug.append(payload)
            return True
        elif packet.packet_type == PacketType.data:
            self._sct_data = payload
        return False

    def _sct_send(self):
        with logging.LogCall(__file__, "_sct_send", self.__class__):
            with SCTSock(create_socket(self.get_url(), self.get_port()), timeout=self.request.max_timeout) as sock:
                sock.send_init(self.request.setting_version)
                while self._sct_loop(sock):
                    pass


