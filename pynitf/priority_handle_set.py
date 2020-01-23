import collections

class PriorityHandleSet(collections.abc.Set):
    def __init__(self):
        self.handle_set = collections.defaultdict(lambda : set())

    def __contains__(self, itm):
        return itm[0] in self.handle_set[itm[1]]

    def __len__(self):
        res = 0
        for t in self.handle_set.values():
            res += len(t)
        return res

    def __iter__(self):
        for k in sorted(self.handle_set.keys(), reverse=True):
            for h in self.handle_set[k]:
                yield (h, k)

    @classmethod
    def _from_iterable(cls, it):
        obj = cls()
        for i in it:
            obj.add_handle(i[0],priority_order=i[1])
        return obj

    def __copy__(self):
        '''Copy the PrioritySet. This is a shallow copy, we have our our
        handle set but all the objects in it are the same as the original
        set.'''
        return self.__class__._from_iterable(iter(self))
    
    def add_handle(self, h, priority_order=0):
        '''Add a handler. The higher priority_order (larger number) items are
        tried first.'''
        self.handle_set[priority_order].add(h)

    def discard_handle(self, h):
        '''Discard the handle h. It is ok if h isn't actually in the set 
        of handles.'''
        for k in sorted(self.handle_set.keys()):
            self.handle_set[k].discard(h)

    def clear(self):
        '''Remove all handles in the set.'''
        self.handle_set.clear()

    @classmethod
    def default_handle_set(cls):
        '''Return the default set of handlers to use.'''
        if(not hasattr(cls, "_default_handle_set")):
            cls._default_handle_set = cls()
        return cls._default_handle_set
    
    @classmethod            
    def add_default_handle(cls, h, priority_order=0):
        '''Add the given handle to the default set of handlers.  The 
        higher priority_order (larger number) items are tried first.'''
        cls.default_handle_set().add_handle(h, priority_order)

    @classmethod            
    def discard_default_handle(cls, h):
        '''Discard the handle h from the default list. It is ok if h isn't 
        actually in the set of handles.'''
        cls.default_handle_set().discard_handle(h)

    def handle(self, *args, **keywords):
        '''Find the first handle that says it can process the given arguments,
        and return the results from that handle.'''
        for (h, p) in self:
            could_handle, res = self.handle_h(h, *args, **keywords)
            if(could_handle):
                return res
        raise RuntimeError("No handle was found. args=%s, keywords=%s" % (args, keywords))

    def handle_h(self, h, *args, **keywords):
        raise NotImplementedError
        
        
__all__ = ["PriorityHandleSet",]        
