"""
    Behavior Tree for Pattern Matching...

    Main module that provide a match object...
"""

import collections as c
from treematching.matchcontext import *
from treematching.debug import *

def walk(tree, uid=[(0, 0)]) -> object:
    """
    Bottom-up walker
    """
    #yield ('enter', None, 0, uid)
    depth, parent = uid[-1]
    nchild = 0
    if isinstance(tree, c.Mapping):
        lsk = list(sorted(tree.keys()))
        len_dict = len(lsk)
        #if len_dict:
        #    yield ('enter_dict', None, 2, uid)
        for k in lsk:
            # value, going depth
            nuid = uid + [(depth + 1, nchild)]
            yield from walk(tree[k], nuid)
            # key
            yield ('key', k, 1, nuid)
            nchild += 1
        # dict
        if len_dict:
            yield ('dict', tree, 2, uid)
    elif isinstance(tree, c.Iterable) and type(tree) not in {str, bytes}:
        ls = enumerate(tree)
        len_ls = len(tree)
        #if len_ls:
        #    yield ('enter_list', None, 2, uid)
        for idx, it in ls:
            # value, going depth
            nuid = uid + [(depth + 1, nchild)]
            yield from walk(it, nuid)
            # idx
            yield ('idx', idx, 1, nuid)
            nchild += 1
        # list
        if len_ls:
            yield ('list', tree, 2, uid)
    if hasattr(tree, '__dict__'):
        attrs = vars(tree)
        len_attr = len(attrs)
        #if len_attr:
        #    yield ('enter_attrs', None, 4, uid)
        for k in sorted(attrs.keys()):
            # value, going depth
            nuid = uid + [(depth + 1, nchild)]
            yield from walk(attrs[k], nuid)
            # attr
            yield ('attr', k, 3, nuid)
            nchild += 1
        # attrs
        if len_attr:
            yield ('attrs', attrs, 4, uid)
    # value
    # only for scalar
    scalar_type = {int, float, str, bytes, bool}
    if type(tree) in scalar_type:
        yield ('value', tree, 5, uid)
    # type
    yield ('type', tree, 6, uid)

class MatchingBTree:
    def __init__(self, bt):
        self.state = State.RUNNING
        self.bt = bt

    def do(self, data, ctx, user_data) -> State:
        log("MatchingBTree")
        return self.bt.do(data, ctx, user_data)

    def match(self, tree, user_data=None):
        glist = []
        match = []
        for idx, it in enumerate(walk(tree)):
            log(repr(it))
            log("LEN // %d" % len(glist))
            glist.append(MatchContext())
            dlist = []
            # TODO: idx?
            for idx, g in enumerate(glist):
                log("MATCH TEST %d" % idx)
                r = self.do(it, g, user_data)
                log("MATCH RES %d %s" % (id(g), repr(r)))
                if r == State.FAILED:
                    log("NOMATCH ADD REMOVE: %d" % idx)
                    dlist.append(g)
                if r == State.SUCCESS:
                    log("MATCH ADD REMOVE: %d" % idx)
                    match.append(g)
                    dlist.append(g)
            for d in dlist:
                log("DO REMOVE: %d" % id(d))
                glist.remove(d)
            log("%s\n" % ('-' * 20))
        return match
###
