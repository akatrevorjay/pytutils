import collections
import re

import six


class AttrDict(dict):
    """
    >>> m = AttrDict(omg=True, whoa='yes')
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


Messenger = AttrDict


class ProxyMutableMapping(collections.MutableMapping):
    """Proxies access to an existing dict-like object."""

    def __init__(self, mapping, fancy_repr=True, dictify_repr=False):
        """
        :param collections.MutableMapping mapping: Dict-like object to wrap
        :param bool fancy_repr: If True, show fancy repr, otherwise just show dict's
        :param bool dictify_repr: If True, cast mapping to a dict on repr
        """
        self.__mapping = mapping
        self.__fancy_repr = fancy_repr
        self.__dictify_repr = dictify_repr

    def __repr__(self):
        if not self.__fancy_repr:
            return '%s' % dict(self)

        mapping = self.__mapping
        if self.__dictify_repr:
            mapping = dict(mapping)

        return '<%s %s>' % (self.__class__.__name__, mapping)

    def __contains__(self, item):
        return item in self.__mapping

    def __getitem__(self, item):
        return self.__mapping[item]

    def __setitem__(self, key, value):
        self.__mapping[key] = value

    def __delitem__(self, key):
        del self.__mapping[key]

    def __iter__(self):
        return iter(self.__mapping)

    def __len__(self):
        return len(self.__mapping)


class PrefixedProxyMutableMapping(ProxyMutableMapping):

    def __init__(self, prefix, mapping, only_prefixed=True, fancy_repr=True, dictify_repr=False):
        """
        :param str prefix: Prefix to add/remove from keys.
        :param collections.MutableMapping mapping: Dict-like object to wrap
        :param bool fancy_repr: If True, show fancy repr, otherwise just show dict's
        :param bool dictify_repr: If True, cast mapping to a dict on repr
        """
        self.__prefix = prefix
        self.__prefix_len = len(prefix)
        self.__only_prefixed = only_prefixed
        super(PrefixedProxyMutableMapping, self).__init__(
            mapping,
            fancy_repr=fancy_repr,
            dictify_repr=dictify_repr,
        )

    def __key_add_prefix__(self, key):
        return self.__prefix + key

    def __key_remove_prefix__(self, key):
        return key[self.__prefix_len:]

    def __key_allowed__(self, key):
        if self.__only_prefixed:
            if isinstance(key, six.string_types):
                if not key.startswith(self.__prefix):
                    return False
            else:
                return False
        return True

    def __iter__(self):
        orig_iter = super(PrefixedProxyMutableMapping, self).__iter__()
        return (self.__key_remove_prefix__(key) for key in orig_iter if self.__key_allowed__(key))

    def __contains__(self, item):
        item = self.__key_add_prefix__(item)
        return super(PrefixedProxyMutableMapping, self).__contains__(item)

    def __getitem__(self, item):
        item = self.__key_add_prefix__(item)
        return super(PrefixedProxyMutableMapping, self).__getitem__(item)

    def __setitem__(self, item, value):
        item = self.__key_remove_prefix__(item)
        return super(PrefixedProxyMutableMapping, self).__setitem__(item, value)

    def __delitem__(self, item):
        item = self.__key_add_prefix__(item)
        return super(PrefixedProxyMutableMapping, self).__delitem__(item)


class MultiDict(collections.OrderedDict):
    """Simple multi-value ordered dict."""
    _unique = 0

    def __setitem__(self, key, val):
        if isinstance(val, dict) and key in self:
            self._unique += 1
            key += str(self._unique)
        dict.__setitem__(self, key, val)


multidict = MultiDict


def format_dict_recursively(
        mapping, raise_unresolvable=True, strip_unresolvable=False, conversions={
            'True': True,
            'False': False
        }
):
    """Format each string value of dictionary using values contained within
    itself, keeping track of dependencies as required.

    Also converts any formatted values according to conversions dict.

    Example:

    >>> c = dict(wat='wat{omg}', omg=True)
    >>> format_dict_recursively(c)
    {'omg': True, 'wat': 'watTrue'}

    Dealing with missing (unresolvable) keys in format strings:

    >>> c = dict(wat='wat{omg}', omg=True, fail='no{whale}')
    >>> format_dict_recursively(c)
    Traceback (most recent call last):
        ...
    ValueError: Impossible to format dict due to missing elements: {'fail': ['whale']}
    >>> format_dict_recursively(c, raise_unresolvable=False)
    {'omg': True, 'wat': 'watTrue', 'fail': 'no{whale}'}
    >>> format_dict_recursively(c, raise_unresolvable=False, strip_unresolvable=True)
    {'omg': True, 'wat': 'watTrue'}

    :param dict mapping: Dict.
    :param bool raise_unresolvable: Upon True, raises ValueError upon an unresolvable key.
    :param bool strip_unresolvable: Upon True, strips unresolvable keys.
    :param dict conversions: Mapping of {from: to}.
    """
    if conversions is None:
        conversions = {}

    ret = {}

    # Create dependency mapping
    deps = {}
    for k, v in mapping.items():
        # Do not include multiline values in this to avoid KeyErrors on actual
        # .format below
        if isinstance(v, six.string_types) and '\n' not in v:
            # Map key -> [*deps]
            # This is a bit naive, but it works well.
            deps[k] = re.findall(r'\{(\w+)\}', v)
        else:
            ret[k] = v

    while len(ret) != len(mapping):
        ret_key_count_at_start = len(ret)
        sret = set(ret)
        keys = set(mapping) - sret

        for k in keys:
            needed = (x not in ret for x in deps[k])
            if any(needed):
                continue

            ret[k] = mapping[k].format(**ret)

            if ret[k] in conversions:
                ret[k] = conversions[ret[k]]

        # We have done all that we can here.
        if ret_key_count_at_start == len(ret):
            if not raise_unresolvable:
                if not strip_unresolvable:
                    # backfill
                    ret.update({k: mapping[k] for k in keys})
                break

            missing = {k: [x for x in deps[k] if x not in ret]}
            raise ValueError('Impossible to format dict due to missing elements: %r' % missing)

    return ret


class ProxyMutableAttrDict(dict):

    @property
    def _wrap_as(self):
        return self.__class__

    def __getattr__(self, key):
        if not key.startswith('_'):
            try:
                val = self.__mapping[key]
                return val
            except KeyError:
                # in py3 I'd chain these
                raise AttributeError(key)

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            if isinstance(value, collections.Mapping) and not isinstance(value, self._wrap_as):
                value = self.__class__(value)

            try:
                self[key] = value
            except KeyError:
                # in py3 I'd chain these
                raise AttributeError(key)

        return super(ProxyMutableAttrDict, self).__setattr__(key, value)


class RecursiveProxyAttrDict(ProxyMutableMapping):
    __getattr__ = ProxyMutableMapping.__getitem__
    __setattr__ = ProxyMutableMapping.__setitem__

    def __getitem__(self, name):
        val = self.__getitem__(name)

        if isinstance(val, collections.Mapping) and not isinstance(val, self.__class__):
            val = self.__class__(val)

        raise AttributeError(name)
