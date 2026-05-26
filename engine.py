# ============================================================
#  SCRABBLE-X Engine v2.0
#  Trie + Backtracking + Scoring + Blank Tile (?  wildcard)
# ============================================================

# Nilai huruf resmi Scrabble (English Standard)
LETTER_SCORES = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4,
    'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1,
    'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1,
    's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8,
    'y': 4, 'z': 10, '?': 0
}

MAX_RACK_SIZE = 7


class TrieNode:
    __slots__ = ('children', 'is_word')

    def __init__(self):
        self.children: dict[str, 'TrieNode'] = {}
        self.is_word: bool = False


class ScrabbleEngine:
    def __init__(self):
        self.root = TrieNode()
        self._word_count = 0

    # ----------------------------------------------------------
    #  Insert
    # ----------------------------------------------------------
    def insert(self, word: str) -> None:
        word = word.strip().lower()
        if len(word) < 2:          # minimal 2 huruf di Scrabble
            return
        if not word.isalpha():     # skip kata dengan karakter aneh
            return
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        if not node.is_word:
            node.is_word = True
            self._word_count += 1

    @property
    def dictionary_size(self) -> int:
        return self._word_count

    # ----------------------------------------------------------
    #  Scoring helper
    # ----------------------------------------------------------
    @staticmethod
    def score_word(word: str) -> int:
        """Hitung skor kata berdasarkan nilai huruf standar Scrabble."""
        return sum(LETTER_SCORES.get(c, 0) for c in word.lower())

    # ----------------------------------------------------------
    #  Backtracking search (support blank tile '?')
    # ----------------------------------------------------------
    def find_all_words(self, rack: str, min_length: int = 2) -> list[dict]:
        """
        Cari semua kata valid dari tile yang diberikan.

        Parameters
        ----------
        rack        : string tile, gunakan '?' untuk blank tile (wildcard)
        min_length  : panjang minimum kata (default 2)

        Returns
        -------
        list of dict  ->  [{"word", "score", "length", "uses_blank"}, ...]
        diurutkan berdasarkan skor tertinggi, lalu panjang kata.
        """
        rack = rack.strip().lower()

        # Validasi karakter
        valid_chars = set('abcdefghijklmnopqrstuvwxyz?')
        invalid = set(rack) - valid_chars
        if invalid:
            raise ValueError(f"Tile tidak valid: {', '.join(invalid).upper()}")

        found: dict[str, dict] = {}  # word -> best result

        def backtrack(node: TrieNode, path: str, tile_rack: list, score: int, used_blank: bool):
            if node.is_word and len(path) >= min_length:
                if path not in found or found[path]['score'] < score:
                    found[path] = {
                        'word':       path,
                        'score':      score,
                        'length':     len(path),
                        'uses_blank': used_blank,
                    }

            for char, next_node in node.children.items():
                # Gunakan tile asli
                if char in tile_rack:
                    tile_rack.remove(char)
                    backtrack(next_node, path + char, tile_rack,
                              score + LETTER_SCORES.get(char, 0), used_blank)
                    tile_rack.append(char)

                # Gunakan blank tile sebagai wildcard (nilai = 0)
                elif '?' in tile_rack:
                    tile_rack.remove('?')
                    backtrack(next_node, path + char, tile_rack,
                              score, True)   # blank = 0 pts
                    tile_rack.append('?')

        backtrack(self.root, '', list(rack), 0, False)

        results = sorted(
            found.values(),
            key=lambda x: (-x['score'], -x['length'], x['word'])
        )
        return results