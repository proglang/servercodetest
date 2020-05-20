from multiprocessing import Lock


class SystemLockHandler:
    locks = {}
    global_lock = tuple(Lock() for i in range(10))

    @classmethod
    def register(cls, key: str):
        """ register a lock with a specific key
        this function must be called BEFORE any process is forked
        """
        cls.locks[key] = Lock()

    @classmethod
    def get(self, key: str):
        """get Lock with specific key
        """
        return self.locks[key]

    @classmethod
    def get_global(cls, index=0):
        return cls.global_lock[index]


LockHandler = SystemLockHandler
