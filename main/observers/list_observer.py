"""
Implement an observer pattern for lists and dictionaries.

A subclasses for dicts and lists are defined which send information
about changes to an observer.

The observer is sent enough information about the change so that the
observer can undo the change, if desired.
"""


class ListObserver(list):
    """
    Send all changes to an observer.
    """

    def __init__(self, value, observer):
        list.__init__(self, value)
        self.observer = None
        self.set_observer(observer)

    def set_observer(self, observer):
        """
        All changes to this list will trigger calls to observer methods.
        """
        self.observer = observer

    def __setitem__(self, key, value):
        """
        Intercept the l[key]=value operations.
        Also covers slice assignment.
        """
        try:
            old_value = self.__getitem__(key)
        except KeyError:
            list.__setitem__(self, key, value)
            self.observer.list_create(self, key)
        else:
            list.__setitem__(self, key, value)
            self.observer.list_set(self, key, old_value)

    def __delitem__(self, key):
        old_value = list.__getitem__(self, key)
        list.__delitem__(self, key)
        self.observer.list_del(self, key, old_value)

    def __setslice__(self, i, j, sequence):
        old_value = list.__getslice__(self, i, j)
        self.observer.list_setslice(self, i, j, sequence, old_value)
        list.__setslice__(self, i, j, sequence)

    def __delslice__(self, i, j):
        old_value = list.__getitem__(self, slice(i, j))
        list.__delslice__(self, i, j)
        self.observer.list_delslice(self, i, old_value)

    def append(self, value):
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaa')
        list.append(self, value)
        self.observer.list_append(self)

    def pop(self):
        old_value = list.pop(self)
        self.observer.list_pop(self, old_value)

    def extend(self, new_value):
        list.extend(self, new_value)
        self.observer.list_extend(self, new_value)

    def insert(self, i, element):
        list.insert(self, i, element)
        self.observer.list_insert(self, i, element)

    def remove(self, element):
        index = list.index(self, element)
        list.remove(self, element)
        self.observer.list_remove(self, index, element)

    def reverse(self):
        list.reverse(self)
        self.observer.list_reverse(self)

    def sort(self, cmpfunc=None):
        old_list = self[:]
        list.sort(self, cmpfunc)
        self.observer.list_sort(self, old_list)
