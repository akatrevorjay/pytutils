import collections

_ALL = object()
_sentinel = object()


def traverse_tree(mapping, keys=[_ALL], __level=0):
    """
    Traverse dictionary `mapping` on the specified `traverse_keys`, yielding each node. NOT thread safe.
    If `traverse_tree.ALL` is included in `keys`, then every edge node will be yielded.

    :param mapping collections.Mapping: Dictionary
    :param keys collections.Iterable: Iterable of keys to walk down

    >>> data = {'count': 2,
    ...         'text': '1',
    ...         'kids': [{'count': 3,
    ...                   'text': '1.1',
    ...                   'kids': [{'count': 1,
    ...                             'text': '1.1.1',
    ...                             'kids': [{'count':0,
    ...                                       'text': '1.1.1.1',
    ...                                       'kids': []}]},
    ...                            {'count': 0,
    ...                             'text': '1.1.2',
    ...                             'kids': []},
    ...                            {'count': 0,
    ...                             'text': '1.1.3',
    ...                             'kids': []}]},
    ...                  {'count': 0,
    ...                   'text': '1.2',
    ...                   'kids': []}]}
    >>> traverse_tree(data, 'kids')
    """
    iter_keys = traverse_tree.ALL in keys and mapping.keys() or keys
    for key in iter_keys:
        for child in mapping[key]:
            __level += 1
            yield child
            yield traverse_tree(mapping, child, keys=keys, __level=__level)
            __level -= 1


traverse_tree.ALL = _ALL


def get_tree_node(mapping, key, default=_sentinel, parent=False):
    """
    Fetch arbitrary node from a tree-like mapping structure with traversal help:
    Dimension can be specified via ':'

    Arguments:
        mapping collections.Mapping: Mapping to fetch from
        key str|unicode: Key to lookup, allowing for : notation
        default object: Default value. If set to `:module:_sentinel`, raise KeyError if not found.
        parent bool: If True, return parent node. Defaults to False.

    Returns:
        object: Value at specified key
    """
    key = key.split(':')
    if parent:
        key = key[:-1]

    # TODO Unlist my shit. Stop calling me please.

    node = mapping
    for node in key.split(':'):
        try:
            node = node[node]
        except KeyError as exc:
            node = default
            break

    if node is _sentinel:
        raise exc
    return node


def set_tree_node(mapping, key, value):
    """
    Set arbitrary node on a tree-like mapping structure, allowing for : notation to signify dimension.

    Arguments:
        mapping collections.Mapping: Mapping to fetch from
        key str|unicode: Key to set, allowing for : notation
        value str|unicode: Value to set `key` to
        parent bool: If True, return parent node. Defaults to False.

    Returns:
        object: Parent node.

    """
    basename, dirname = key.rsplit(':', 2)
    parent_node = get_tree_node(mapping, dirname)
    parent_node[basename] = value
    return parent_node


def tree():
    """Extremely simple one-lined tree based on defaultdict."""
    return collections.defaultdict(tree)


class Tree(collections.defaultdict):
    """
    Same extremely simple tree based on defaultdict as `tree`, but implemented as a class for extensibility.
    Use ':' to delve down into dimensions without choosing doors [][][] .
    Supports specifying a namespace that acts as a key prefix.
    """
    namespace = None

    def __init__(self, initial=None, namespace='', initial_is_ref=False):
        if initial is not None and initial_is_ref:
            self.data = initial_is_ref
        self.namespace = namespace
        super(Tree, self).__init__(self.__class__)
        if initial is not None:
            self.update(initial)

    def _namespace_key(self, key, namespace=_sentinel):
        if namespace is _sentinel:
            namespace = self.namespace
        if namespace:
            key = '%s:%s' % (namespace, key)
        return key

    def __setitem__(self, key, value, namespace=None):
        key = self._namespace_key(key, namespace=namespace)
        return set_tree_node(self, key, value)

    def __getitem__(self, key, default=_sentinel, namespace=None):
        key = self._namespace_key(key, namespace=namespace)
        return get_tree_node(self, key, default=default)

    get = __getitem__


class RegistryTree(Tree):

    # Alias
    register = Tree.__setitem__

