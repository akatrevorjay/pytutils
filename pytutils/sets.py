import collections
from .iterators import consume


class TimedValueSet(collections.MutableSet):
    """
    Set that tracks the time a value was added.
    """
    container_factory = set
    added_at_mapping_factory = dict

    # added_at_factory = weakref.WeakKeyDictionary

    def __init__(self, seq=None, container_factory=None, added_at_mapping_factory=None):
        if container_factory:
            self.container_factory = container_factory
        if added_at_mapping_factory:
            self.added_at_mapping_factory = added_at_mapping_factory

        self._store = self.container_factory()
        self._added_at = self.added_at_mapping_factory()
        if seq:
            self.update(seq)

    def __contains__(self, item):
        return item in self._store

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def add(self, value):
        self._store.add(value)
        self._added_at[value] = time.time()

    def discard(self, value):
        self._store.discard(value)
        if value in self._added_at:
            del self._added_at[value]

    def update(self, iterable):
        """Add all values from an iterable (such as a list or file)."""
        # Must comsume generator fully on py3k
        consume(map(self.add, iterable))

    def added_at(self, value, default=None):
        return self._added_at.get(value, default)

