import socket
import struct
import json
import time
import os, sys, signal
import logging

# pylint: disable=import-error
from sctsock import SCTSock, create_socket
from plugin import Plugin
from util import get_traceback

# pylint: enable=import-error

from threading import Thread, Event
import multiprocessing
import multiprocessing.pool
from enum import IntEnum
import signal

class ErrorCodes(IntEnum):
    none = 0
    too_many_connections = 1
    listener_timeout = 2
    execution_timeout = 3
    exception = 4


class Timeout:
    def __init__(self, callback, wait=60):
        self.exit = Event()
        self.timeout = 0
        self.set_time = False
        self.wait = wait
        self.lock = multiprocessing.Lock()
        self.callback = callback
        self.start()

    def reset(self):
        with self.lock:
            self.timeout = time.time()

    def set_timeout_duration(self, val):
        _type = type(val)
        if _type!=int and _type != float:
            return False
        if val <= 0:
            return True
        # upper / lower bound for timeout
        val = min(max(val, 5), 1*60*60) # 1 hour max (in seconds)
        with self.lock:
            self.set_time = True
            self.wait = val
            self.exit.set()
        return True

    def stop(self):
        self.exit.set()

    def start(self):
        self.reset()
        thread = Thread(target=self)
        thread.daemon = True
        thread.start()

    def __call__(self):
        while True:
            _time = 0
            current = time.time()
            with self.lock:
                _time = self.timeout + self.wait
            if _time <= current:
                break
            self.exit.wait(_time - current)
            with self.lock:
                if self.set_time:
                    self.set_time = False
                    self.exit.clear()
                if self.exit.is_set():
                    break
        self.callback()


class TooManyConnectionsError(Exception):
    pass


class Connections:
    def __init__(self, max):
        self._lock = multiprocessing.Lock()
        self._entries = set()
        self._max = max

    def add(self, con):
        with self._lock:
            if len(self._entries) >= self._max:
                raise TooManyConnectionsError
            self._entries.add(con)
            return len(self._entries)

    def remove(self, con):
        with self._lock:
            self._entries.remove(con)

    def apply(self, fn):
        with self._lock:
            for entry in self._entries:
                try:
                    fn(entry)
                except:
                    pass


class ConnectionsWrapper:
    def __init__(self, sock, connections: Connections):
        self.connections = connections
        self.sock = sock

    def __enter__(self):
        self.connections.add(self.sock)

    def __exit__(self, e, msg, tb):
        self.connections.remove(self.sock)
        if e:
            raise


class Listener:
    def __init__(self, on_connect):
        self._on_connect = on_connect

    def run(self):
        listener = create_socket("", 1700, False)
        listener.settimeout(0.5)
        self._exit = Event()
        while not self._exit.is_set():
            try:
                (client, _) = listener.accept()
            except socket.timeout:
                continue
            except:
                break
            sock = SCTSock(client)
            self._on_connect(sock)

    def close(self):
        self._exit.set()


class Main:
    @staticmethod
    def send_data(sock: SCTSock, code: ErrorCodes, data=None):
        sock.send_data({"res": code, "data": data})
        sock.close()

    def __init__(self, threads:int=20, listener_timeout:int=600, request_timeout:int=50):
        self._request_timout = request_timeout

        signal.signal(signal.SIGTERM, self.stop)

        self._pool = multiprocessing.pool.ThreadPool(threads + 1)
        self._lock = multiprocessing.Lock()

        self._plugin = Plugin()
        self._timeout = Timeout(self.stop, listener_timeout)
        self._connections = Connections(threads)
        self._listener = Listener(self.handle_connection)
        self._listener.run()

    def stop(self, signum:int=0, frame=None):
        self._timeout.stop()
        self._listener.close()
        self._connections.apply(lambda con: self.send_data(con, ErrorCodes.listener_timeout))
        self._pool.close()

    def handle_connection(self, sock: SCTSock):
        self._pool.apply_async(self._handle_connection_thread, [sock])
    
    def _set_request_timeout(self, val):
        # don't call this function without locking self._lock first!
        _type = type(val)
        if _type!=int and _type != float:
            return False
        if val <= 0:
            return True
        # upper / lower bound for timeout
        val = min(max(val, 5), 60) # 60 seconds max
        self._request_timout = val
        return True

    def _handle_connection_thread(self, sock: SCTSock):
        try:
            with ConnectionsWrapper(sock, self._connections):
                self._timeout.reset()
                timeout = None
                with self._lock:
                    version = sock.recv().payload
                    if not self._plugin.checkVersion(version):
                        sock.send_init("init")
                        data = sock.recv().payload
                        self._plugin.setSettings(version, data)
                        self._timeout.set_timeout_duration(data.get("main", {}).get("container_timeout", None))
                        self._set_request_timeout(data.get("main", {}).get("code_timeout", None))
                        logging.debug("Settings: %s", str(data))
                    timeout = self._request_timout
                if timeout==None:
                    raise ValueError("timeout must be set!")
    
                sock.send_init("data")
                con_pool = multiprocessing.pool.ThreadPool(1)
                data = sock.recv().payload
                result = con_pool.apply_async(self._plugin.exec, [data]).get( timeout )
                con_pool.close()
                self.send_data(sock, ErrorCodes.none, result)
        except multiprocessing.TimeoutError:
            logging.debug("A timeout occurred while executing user code")
            self.send_data(sock, ErrorCodes.execution_timeout)
        except TooManyConnectionsError:
            logging.info("Too many connections: Maybe increase threadcount.")
            self.send_data(sock, ErrorCodes.too_many_connections)
        except Exception as e:
            traceback = get_traceback(e)
            self.send_data(sock, ErrorCodes.exception, traceback)
            logging.error(str(traceback))
        finally:
            sock.close()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
    logging.info("Startup")
    Main()
    logging.info("Shutdown")
