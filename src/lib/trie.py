from typing import List, Union

from grammar import *

class TrieNode:
    def __init__(self):
        self.depth = None
        self.parent = None
        self.children = {}
        self.is_end_of_word = False
        self.n = 0
        self.symbol = None


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.root.depth = 1

    def insert(self, seq: List[Union[Terminal, NTerminal]]):
        node = self.root
        for symbol in seq:
            if symbol not in node.children:
                node.children[symbol] = TrieNode()
            node.children[symbol].parent = node
            node.children[symbol].depth = node.depth + 1
            node.children[symbol].symbol = symbol
            node = node.children[symbol]
            node.n += 1
        node.is_end_of_word = True

    def find_node_with_max_leaves(self, node: TrieNode):
        if not node.children:
            return node, node.n

        max_leaves_node = node
        max_leaves_count = node.n
        max_depth = node.depth

        for child_node in node.children.values():
            max_node, _ = self.find_node_with_max_leaves(child_node)
            child_leaves_count = max_node.n
            if child_leaves_count >= max_leaves_count and (max_node.depth > max_depth or max_leaves_count == 1):
                max_leaves_count = child_leaves_count
                max_leaves_node = max_node
                max_depth = max_node.depth

        return max_leaves_node, max_leaves_count

    def find_prefix_for_node(self, node):
        prefix = []
        while node != self.root:
            prefix = [node.symbol] + prefix
            node = node.parent
        return prefix

    def find_best_prefix(self):
        max_node, max_leaves = self.find_node_with_max_leaves(self.root)
        return self.find_prefix_for_node(max_node) if max_leaves > 1 else []
