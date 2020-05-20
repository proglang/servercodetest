import json
import re


class Info:
    def __init__(
        self, name: str, uid: str, version: str, description: str, author: str
    ):
        self.name = name
        self.uid = uid
        self.version = version
        self.description = description
        self.author = author

    @classmethod
    def from_file(cls, path: str):
        with open(path) as file:
            return cls.from_file_obj(file)

    @classmethod
    def from_file_obj(cls, file):
        data = json.load(file)
        uid = data["uid"]
        name = data.get("name", uid)
        version = data["version"].replace(" ", "")
        if not re.match(r"^[a-z]{0,1}\d+(|(\.\d+(|\.\d+)))[\w\-]*$", version):
            version = "0.0.0"
        description = data.get("description", "")
        author = data.get("author", "")
        return cls(name, uid, version, description, author)

