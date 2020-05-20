import typing
from util.struct import Base


class Raw(Base):
    """"Struct for Raw Radon Metrics"""

    def __init__(self):
        self.loc = 0
        self.sloc = 0
        self.lloc = 0

    def set(self, loc: int, sloc: int, lloc: int):
        """ Set Data """
        self.loc = loc
        self.sloc = sloc
        self.lloc = lloc


class CyclomaticComplexity(Base):
    """"Struct for cc Radon Metrics"""

    class Entry(Base):
        """Struct for cc Radon metric entry
            Variables:
                - type (str): class, function, method
                - fn (str): function name
                - rank (str): A-F depending on complexity
                - complexity(int): number value of cyclomatic complexity
        """

        def __init__(self, fn: str, typ: str, rank: str, complexity: int):
            self.type = typ
            self.rank = rank
            self.name = fn
            self.complexity = complexity

    def __init__(self):
        self.entries: typing.List[self.Entry,] = []

    def add(self, function, type, complexity, rank):
        """ adds CyclomaticComplexity.Entry"""
        self.entries.append(self.Entry(function, type, rank, complexity))

    def serialize(self) -> tuple:
        return self._serialize(self.entries)


class Output(Base):
    """"Struct for output of Radon Metrics"""

    def __init__(self):
        self.raw: Raw = None
        self.cyclomatic_complexity: CyclomaticComplexity = None

    def serialize(self):
        res = {}
        if self.raw:
            res["raw"] = self.raw
        if self.cyclomatic_complexity:
            res["cc"] = self.cyclomatic_complexity
        return self._serialize(res)
