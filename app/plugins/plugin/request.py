
class _Request:
    """Base Request class.
    DO NOT CHANGE THIS CLASS.
    """
    def __init__(self, token: str, version: str, settings: dict, timeout: int, body:dict):
        self.token: str = token
        self.setting_version = version
        self.settings: dict = settings
        self.max_timeout: int = timeout
        self.populate(body)

    def populate(self, body:dict):
        """add fields which are required by the given plugin
        """
        pass

class Request(_Request):
    """Basic Request which populates commonly used fields
    """
    def populate(self, body:dict):
        self.code: str = body.get("code", "")
        self.test: str = body.get("test", "")
