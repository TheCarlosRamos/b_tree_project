from typing import List, Optional
import icontract

class BTreeNode:
    def __init__(self, t: int, leaf: bool):
        self.t = t
        self.leaf = leaf
        self.keys: List[int] = []
        self.children: List['BTreeNode'] = []

    @icontract.invariant(lambda self: all(self.keys[i] < self.keys[i + 1] for i in range(len(self.keys) - 1)))
    @icontract.invariant(lambda self: (self.leaf and len(self.children) == 0) or (not self.leaf and len(self.children) == len(self.keys) + 1))
    class _:
        pass

    def is_full(self) -> bool:
        return len(self.keys) == 2 * self.t - 1
