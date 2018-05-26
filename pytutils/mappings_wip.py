

class RecursiveProxyAttrDict(pytutils.mappings.ProxyMutableMapping):
    __getattr__ = pytutils.mappings.ProxyMutableMapping.__getitem__
    def __getattr__(self, name):
        try:
            val =  self.__getitem__(name)
            if isinstance(val, collections.Mapping):
                val = self.__class__(val)
        raise AttributeError(name)

    __setattr__ = pytutils.mappings.ProxyMutableMapping.__setitem__

