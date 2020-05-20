import typing
from util.struct import Base


class Text(Base):
    def __init__(self, error: str, text: str):
        self.error = error
        self.text = text


class Mark(Text):
    class Entry(Base):
        def __init__(self, fn, note, points):
            self.note = note
            self.points = points
            self.function = fn

    def __init__(self, error: str, text: str):
        super().__init__(error, text)
        self.success = []
        self.missed = []

    def add(self, fn, note, points, success:bool):
        if success:
            self.success.append(self.Entry(fn, note, points))
        else:
            self.missed.append(self.Entry(fn, note, points))

class Output(Base):
    """"Struct for output of Radon Metrics"""

    def __init__(self):
        self.run: Text = None
        self.pytest: Text = None
        self.mark: Mark = None

    def serialize(self):
        res = {}
        if self.run:
            res["run"] = self.run
        if self.pytest:
            res["pytest"] = self.pytest
        if self.mark:
            res["mark"] = self.mark
        return self._serialize(res)
