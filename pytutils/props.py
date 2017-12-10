
from .memo import lazyclassproperty, lazyperclassproperty, lazyproperty


class classproperty(object):
    """
    Class-level property descriptor factory/decorator.
    """

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class setterproperty(object):

    def __init__(self, func, doc=None):
        self.func = func
        self.__doc__ = doc if doc is not None else func.__doc__

    def __set__(self, obj, value):
        return self.func(obj, value)


