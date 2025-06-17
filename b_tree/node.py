
from typing import List, Optional

class Node:
    def __init__(self, t: int, is_leaf: bool):
        self.t = t
        self.is_leaf = is_leaf
        self.keys: List[int] = []
        self.children: List['Node'] = []
        
        

