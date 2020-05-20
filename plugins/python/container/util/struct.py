import typing


class Base:
    """Base Class for all structs"""

    @classmethod
    def to_serializable(cls, var: typing.Any) -> typing.Any:
        """Return var.serialize() if var is inherited from _Base else None
        Arguments:
            - var: _Base, None
        Returns:
            - var.serialize() or None
        """
        if isinstance(var, Base):
            return var.serialize()
        if isinstance(var, (set,)):
            var = tuple(var)
        if isinstance(var, (int, float, dict, tuple, list, str)):
            return var
        return None

    @classmethod
    def _serialize(cls, obj:typing.Any) -> typing.Any:
        data = cls.to_serializable(obj)
        if isinstance(data, (tuple, list)):
            ret = []
            for entry in data:
                ret.append(cls._serialize(entry))
            return ret
        if isinstance(data, dict):
            ret = {}
            for (key, entry) in data.items():
                ret[cls._serialize(key)] = cls._serialize(entry)
            return ret
        return data


    def serialize(self) -> typing.Any:
        """ Returns a json serializeable object (e.g. string, dict, list)
        Returns:
             - Any
        """
        return self._serialize(self.__dict__)
