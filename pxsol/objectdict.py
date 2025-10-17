import typing


class ObjectDict(dict):
    def __getattr__(self, name: str) -> typing.Any:
        try:
            value = self[name]
            if type(value) == dict:
                value = ObjectDict(value)
                self[name] = value
                return value
            return value
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: typing.Any) -> None:
        self[name] = value
