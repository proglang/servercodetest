import typing
from subprocess import Popen as _Popen, PIPE as _Pipe, TimeoutExpired as _TimeoutExpired

class Popen:
    def __init__(self, *args, env=None, cwd=".", timeout=60):
        self._args = args
        self._env = env
        self._cwd = cwd
        self._timeout = timeout

        self.code = None
        self.data = None
        self.error = None
        self.isTimeout = None

        self.run()

    def __str__(self):
        return f"Popen result: {self.code}"

    def run(self):
        try:
            p = _Popen(
                self._args,
                stdout=_Pipe,
                stderr=_Pipe,
                text=True,
                env=self._env,
                cwd=self._cwd,
            )
            (out, err) = p.communicate(timeout=self._timeout)
            code = p.wait(timeout=1)
            self.isTimeout = False

            self.data = out
            self.code = code
            self.error = err
        except _TimeoutExpired as e:
            self.isTimeout = True
            self.code = -1
            self.data = ""
            self.error = f"{self._args[0]}: Timeout({e.timeout})"
        except:
            raise Exception(str([self._args, self._env, self._cwd]))
