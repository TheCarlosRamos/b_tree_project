from typing import Optional, Dict, Any
from .b_tree_node import BTreeNode
import icontract


class BTree:
    def __init__(self, t: int):
        self.t = t
        self.root = BTreeNode(t, True)
        self._old_state: Optional[Dict[str, Any]] = None

    def _get_height(self, node: Optional[BTreeNode] = None) -> int:
        if node is None:
            node = self.root
        if not node.keys:
            return 0
        if node.leaf:
            return 1
        return 1 + max(self._get_height(child) for child in node.children)

    @icontract.require(lambda self, key: not self.contains(key),
                       "Key already exists in the tree")
    def insert(self, key: int):
        if self.root.is_full():
            new_root = BTreeNode(self.t, False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root
            self.insert_non_full(new_root, key)
        else:
            self.insert_non_full(self.root, key)

    def insert_non_full(self, node: BTreeNode, key: int):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(0)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if node.children[i].is_full():
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self.insert_non_full(node.children[i], key)

    def split_child(self, parent: BTreeNode, index: int):
        t = self.t
        full_child = parent.children[index]
        new_node = BTreeNode(t, full_child.leaf)
        
        parent.keys.insert(index, full_child.keys[t - 1])
        parent.children.insert(index + 1, new_node)
        
        new_node.keys = full_child.keys[t:(2 * t - 1)]
        full_child.keys = full_child.keys[0:t - 1]
        
        if not full_child.leaf:
            new_node.children = full_child.children[t:(2 * t)]
            full_child.children = full_child.children[0:t]

    @icontract.require(lambda self, key: self.contains(key),
                       "Key does not exist in the tree")
    @icontract.ensure(lambda self: len(self.root.keys) >= 1 or len(self.root.children) == 0,
                      "Root must have at least 1 key or be empty")
    def delete(self, key: int):
        self._delete(self.root, key)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete(self, node: BTreeNode, key: int):
        t = self.t
        idx = 0
        while idx < len(node.keys) and key > node.keys[idx]:
            idx += 1

        if idx < len(node.keys) and node.keys[idx] == key:
            if node.leaf:
                node.keys.pop(idx)
            else:
                if len(node.children[idx].keys) >= t:
                    pred = self._get_predecessor(node, idx)
                    node.keys[idx] = pred
                    self._delete(node.children[idx], pred)
                elif len(node.children[idx + 1].keys) >= t:
                    succ = self._get_successor(node, idx)
                    node.keys[idx] = succ
                    self._delete(node.children[idx + 1], succ)
                else:
                    self._merge(node, idx)
                    self._delete(node.children[idx], key)
        elif not node.leaf:
            if len(node.children[idx].keys) < t:
                self._fill(node, idx)
                if idx > len(node.keys):
                    idx -= 1
            self._delete(node.children[idx], key)

    def _get_predecessor(self, node: BTreeNode, idx: int) -> int:
        current = node.children[idx]
        while not current.leaf:
            current = current.children[-1]
        return current.keys[-1]

    def _get_successor(self, node: BTreeNode, idx: int) -> int:
        current = node.children[idx + 1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]

    def _merge(self, node: BTreeNode, idx: int):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        child.keys.append(node.keys.pop(idx))
        child.keys.extend(sibling.keys)
        
        if not child.leaf:
            child.children.extend(sibling.children)
        
        node.children.pop(idx + 1)

    def _fill(self, node: BTreeNode, idx: int):
        t = self.t
        if idx > 0 and len(node.children[idx - 1].keys) >= t:
            self._borrow_from_prev(node, idx)
        elif idx < len(node.children) - 1 and len(node.children[idx + 1].keys) >= t:
            self._borrow_from_next(node, idx)
        else:
            if idx < len(node.children) - 1:
                self._merge(node, idx)
            else:
                self._merge(node, idx - 1)

    def _borrow_from_prev(self, node: BTreeNode, idx: int):
        child = node.children[idx]
        sibling = node.children[idx - 1]
        
        child.keys.insert(0, node.keys[idx - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        
        node.keys[idx - 1] = sibling.keys.pop()

    def _borrow_from_next(self, node: BTreeNode, idx: int):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        child.keys.append(node.keys[idx])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        
        node.keys[idx] = sibling.keys.pop(0)

    def contains(self, key: int) -> bool:
        return self.search(self.root, key) is not None

    def search(self, node: Optional[BTreeNode], key: int) -> Optional[BTreeNode]:
        if node is None:
            return None
            
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
            
        if i < len(node.keys) and node.keys[i] == key:
            return node
            
        if node.leaf:
            return None
            
        return self.search(node.children[i], key)

    def _validate_btree_properties(self) -> bool:
        return self._validate_node(self.root, True)

    @icontract.invariant(lambda self: self._validate_btree_properties())
    class _:
        pass

    def _validate_node(self, node: BTreeNode, is_root: bool) -> bool:
        t = self.t
        
        if is_root:
            if not (0 <= len(node.keys) <= 2 * t - 1):
                return False
        else:
            if not (t - 1 <= len(node.keys) <= 2 * t - 1):
                return False
        
        for i in range(len(node.keys) - 1):
            if node.keys[i] >= node.keys[i + 1]:
                return False
        
        if not node.leaf:
            if len(node.children) != len(node.keys) + 1:
                return False
            
            for i in range(len(node.keys)):
                if not (self._validate_node(node.children[i], False) and 
                        all(k < node.keys[i] for k in self._get_all_keys(node.children[i]))):
                    return False
                
                if not (self._validate_node(node.children[i + 1], False) and 
                        all(k > node.keys[i] for k in self._get_all_keys(node.children[i + 1]))):
                    return False
        
        return True

    def _get_all_keys(self, node: BTreeNode) -> list:
        keys = []
        if node.leaf:
            return node.keys.copy()
        for i, child in enumerate(node.children):
            keys.extend(self._get_all_keys(child))
            if i < len(node.keys):
                keys.append(node.keys[i])
        return keys
