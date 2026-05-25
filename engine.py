class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class ScrabbleEngine:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True

    def find_all_words(self, rack):
        found_words = set()
        def backtrack(node, path, current_rack):
            if node.is_word:
                found_words.add(path)
            for char, next_node in node.children.items():
                if char in current_rack:
                    remaining = list(current_rack)
                    remaining.remove(char)
                    backtrack(next_node, path + char, remaining)
        backtrack(self.root, "", list(rack.lower()))
        return sorted(list(found_words), key=len, reverse=True)