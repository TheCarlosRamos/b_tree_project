import unittest
from b_tree.b_tree import BTree
from b_tree.b_tree_node import BTreeNode
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from b_tree.b_tree import BTree
from b_tree.b_tree_node import BTreeNode

class TestBTree(unittest.TestCase):
    def setUp(self):
        self.tree = BTree(t=2)
        self.sample_keys = [10, 20, 5, 6, 12, 30, 7, 17]
        self.large_dataset = list(range(1, 100))

    def test_insertion_and_search(self):
        for key in self.sample_keys:
            self.tree.insert(key)

        for key in self.sample_keys:
            self.assertTrue(self.tree.contains(key), f"Key {key} should be in tree")
        self.assertFalse(self.tree.contains(100), "Key 100 should not be in tree")
        self._test_key_ordering(self.tree.root)

    def test_deletion(self):
        for key in self.large_dataset:
            self.tree.insert(key)

        for key in self.large_dataset:
            self.assertTrue(self.tree.contains(key), f"Key {key} should exist before deletion")
            self.tree.delete(key)
            self.assertFalse(self.tree.contains(key), f"Key {key} should be deleted")

        self.assertEqual(len(self.tree.root.keys), 0, "Tree should be empty after all deletions")
        self.assertTrue(self.tree.root.leaf, "Root should be leaf after all deletions")

    def test_all_leaves_at_same_level(self):
        for key in self.sample_keys:
            self.tree.insert(key)

        leaves_depth = set()
        self._collect_leaves_depth(self.tree.root, 0, leaves_depth)
        self.assertEqual(len(leaves_depth), 1, f"All leaves should be at same depth. Found depths: {leaves_depth}")

    def test_node_key_limits(self):
        for key in self.large_dataset:
            self.tree.insert(key)
            self._validate_node_limits(self.tree.root)

        for key in self.large_dataset[:50]:
            self.tree.delete(key)
            self._validate_node_limits(self.tree.root)

    def test_insert_duplicate_key(self):
        self.tree.insert(10)
        with self.assertRaises(AssertionError):
            self.tree.insert(10)

    def test_delete_nonexistent_key(self):
        with self.assertRaises(AssertionError):
            self.tree.delete(99)

    def test_split_root_increases_height(self):
        self.tree = BTree(t=2)
        self.assertEqual(self._get_tree_height(), 0, "Altura inicial deve ser 0")
        self.tree.insert(1)
        self.assertEqual(self._get_tree_height(), 1, "Altura deve ser 1 após primeira inserção")
        self.tree.insert(2)
        self.assertEqual(self._get_tree_height(), 1, "Altura deve permanecer 1")
        self.tree.insert(3)
        self.assertEqual(self._get_tree_height(), 2, "Altura deve ser 2 após split da raiz")
        self.assertEqual(len(self.tree.root.keys), 1, "Raiz deve ter 1 chave após split")
        self.assertEqual(len(self.tree.root.children), 2, "Raiz deve ter 2 filhos após split")

    def test_merge_root_decreases_height(self):
        for key in [1, 2, 3, 4]:
            self.tree.insert(key)
        
        initial_height = self._get_tree_height()
        self.tree.delete(4)
        self.tree.delete(3)
        self.tree.delete(2)
        self.assertEqual(self._get_tree_height(), initial_height - 1, "Tree height should decrease by 1 after root merge")

    def _collect_leaves_depth(self, node: BTreeNode, current_depth: int, depths: set):
        if node.leaf:
            depths.add(current_depth)
        else:
            for child in node.children:
                self._collect_leaves_depth(child, current_depth + 1, depths)

    def _validate_node_limits(self, node: BTreeNode):
        t = self.tree.t
        
        if node == self.tree.root:
            self.assertTrue(0 <= len(node.keys) <= 2 * t - 1)
        else:
            self.assertTrue(t - 1 <= len(node.keys) <= 2 * t - 1)

        if not node.leaf:
            if node == self.tree.root:
                self.assertTrue(2 <= len(node.children) <= 2 * t)
            else:
                self.assertTrue(t <= len(node.children) <= 2 * t)
            
            for child in node.children:
                self._validate_node_limits(child)

    def _test_key_ordering(self, node: BTreeNode):
        for i in range(len(node.keys) - 1):
            self.assertLess(node.keys[i], node.keys[i + 1])

        if not node.leaf:
            for i, child in enumerate(node.children):
                self._test_key_ordering(child)
                if i > 0:
                    self.assertLess(node.keys[i - 1], child.keys[0])
                if i < len(node.keys):
                    self.assertGreater(node.keys[i], child.keys[-1])

    def _get_tree_height(self) -> int:
        return self.tree._get_height()

if __name__ == "__main__":
    unittest.main(verbosity=2)
