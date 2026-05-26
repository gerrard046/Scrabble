# ============================================================
#  SCRABBLE-X Utils v2.0
#  Fungsi-fungsi yang dipakai bersama oleh main.py dan api.py
# ============================================================

from pathlib import Path
from engine import ScrabbleEngine

DICTIONARY_PATH = Path(__file__).parent / 'data' / 'dictionary.txt'


def load_dictionary(engine: ScrabbleEngine) -> int:
    """
    Muat kamus ke engine Trie.
    Raises FileNotFoundError jika dictionary.txt tidak ditemukan.
    Returns jumlah kata yang berhasil dimuat.
    """
    if not DICTIONARY_PATH.exists():
        raise FileNotFoundError(
            f"Kamus tidak ditemukan di: {DICTIONARY_PATH}\n"
            "Pastikan file 'data/dictionary.txt' ada di direktori proyek."
        )

    with open(DICTIONARY_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            engine.insert(line.strip())

    return engine.dictionary_size


def group_by_length(results: list[dict]) -> dict[int, list[dict]]:
    """
    Kelompokkan hasil pencarian berdasarkan panjang kata.

    Returns
    -------
    dict  ->  {length: [{"word", "score", "length", "uses_blank"}, ...]}
    tiap grup sudah terurut berdasarkan skor tertinggi.
    """
    grouped: dict[int, list] = {}
    for item in results:
        length = item['length']
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(item)
    return grouped


def validate_rack(rack: str, max_size: int = 7) -> tuple[bool, str]:
    """
    Validasi input tile rack.

    Returns
    -------
    (is_valid: bool, error_message: str)
    """
    if not rack:
        return False, "Rack tidak boleh kosong!"
    if len(rack) > max_size:
        return False, f"Maksimal {max_size} tile dalam Scrabble! Kamu input {len(rack)} tile."
    valid_chars = set('abcdefghijklmnopqrstuvwxyz?')
    invalid = set(rack.lower()) - valid_chars
    if invalid:
        return False, f"Karakter tidak valid: {', '.join(c.upper() for c in invalid)}"
    return True, ""
