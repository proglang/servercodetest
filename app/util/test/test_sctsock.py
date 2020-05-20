from ..sctsock import SCTSock, Packet, _Packet, PacketType, create_socket
import socket
import pytest

DATA = (b"1", "2", "", b"", {"a": 1}, [1, 2], True, None)


def test_Packet():
    for data in DATA:
        for t in PacketType:
            p = _Packet(t, data)
            assert p.get_payload() == data
            assert p.packet_type == t


class CallbackServer:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __enter__(self):
        self._sock.bind(("", 1234))
        return self

    def __exit__(self, e, msg, tb):
        self._sock.close()

    def listen(self):
        self._sock.listen(5)
        while True:
            try:
                (client, _) = self._sock.accept()
            except:
                break
            try:
                while True:
                    data = client.recv(1024)
                    if len(data) == 0:
                        break
                    client.send(data)
            except:
                pass


@pytest.fixture(autouse=True)
def callback_server():
    from threading import Thread

    with CallbackServer() as server:
        thread = Thread(target=server.listen)
        thread.daemon = True
        thread.start()
        yield server


def test_SCTSock():
    client = create_socket("localhost", 1234)
    with SCTSock(client) as sock:
        for data in DATA:
            sock.send_init(data)
            packet = sock.recv()
            assert data == packet.payload
            assert packet.packet_type == PacketType.init

            sock.send_debug(data)
            packet = sock.recv()
            assert data == packet.payload
            assert packet.packet_type == PacketType.debug

            sock.send_data(data)
            packet = sock.recv()
            assert data == packet.payload
            assert packet.packet_type == PacketType.data
