from collections.abc import MutableMapping


class NestedDict(MutableMapping):

    def __init__(self, root=True):
        super().__init__()
        self._val = {}
        self._found = False
        self._root = root

    def __getitem__(self, item):
        return self._val.__getitem__(item)

    def __setitem__(self, branch_key, value):
        if isinstance(branch_key, tuple):
            branch, key = branch_key
            for k, v in self._val.items():

                if v and isinstance(v, dict):
                    n = NestedDict(root=False)
                    n._val = self._val[k]
                    n[branch_key] = value
                    self._found = n._found if n._found else self._found

                if k == branch:
                    self._found = True
                    if not self._val[branch]:
                        self._val[branch] = {}
                    self._val[branch][key] = value

            if self._root:
                if self._found:
                    self._found = False
                else:
                    raise KeyError

        else:
            self._val.__setitem__(branch_key, value)
            return True

    def __delitem__(self, key):
        self._val.__delitem__(key)

    def __iter__(self):
        return self._val.__iter__()

    def __len__(self):
        return self._val.__len__()

    # def get_val_at_nested_key(self, d: dict, key, is_root=True, found_vals=list):
    #     if is_root:
    #         found_vals = []
    #
    #     for k, v in d.items():
    #         if isinstance(v, dict):
    #             found_vals = self.get_val_at_nested_key(v, key, is_root=False, found_vals=found_vals)
    #         else:
    #             pass
    #
    #         if k == key:
    #             found_vals.append(v)
    #             print('{0}: {1}'.format(k, v))
    #
    #     if is_root:
    #         return found_vals
