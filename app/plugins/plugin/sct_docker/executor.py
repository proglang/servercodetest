from ..docker import Executor as Executor_Docker
from ..sct import Executor as Executor_SCT


class Executor(Executor_Docker, Executor_SCT):
    """ This Executor manages Docker containers and communicates to them with the SCT protocol.
        you need to implement get_port if you don't want to use the default port (1700).

        you need to call 'execute' at the top of your execute Method.
    """
    def __init__(self, *a, **kw):
        Executor_Docker.__init__(self, *a, **kw)
        Executor_SCT.__init__(self, *a, **kw)

    def get_url(self):
        return self.get_container_name()

    def get_port(self) -> int:
        return 1700

    def execute(self):
        Executor_Docker.execute(self)
        Executor_SCT.execute(self)

