# This is from http://code.activestate.com/recipes/528879-weak-key-and-value-dictionary/.
# This basically combines WeakKeyDict and WeakValueDict

import weakref


class WeakKeyValueDict(weakref.WeakKeyDictionary):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Override __setitem__ to store a weak reference to the value
    def __setitem__(self, key, value):
        super().__setitem__(key, weakref.ref(value))

    # Override __getitem__ to dereference the value and check if it's still alive
    def __getitem__(self, key):
        weak_value = super().__getitem__(key)
        value = weak_value()
        if value is None:
            # The value was garbage collected, so remove the entry
            del self[key]
            raise KeyError(key)
        return value

    # Override items() to return live key-value pairs
    def items(self):
        return [(k, v()) for k, v in super().items() if v() is not None]

    # Override values() to return live values
    def values(self):
        return [v() for v in super().values() if v() is not None]

    # You can also override other methods like get(), pop(), etc., for full compatibility
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key, default=object()):
        if default is not object():
            try:
                value = self[key]
            except KeyError:
                return default
        else:
            value = self[key]  # Let KeyError be raised if key is not present

        del self[key]
        return value


__all__ = [
    "WeakKeyValueDict",
]
