#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  SCRABBLE-X CLI v2.0
#  Main entry point -- jalankan di terminal
# ============================================================
import sys
import io

# Force UTF-8 output di Windows agar emoji & box chars muncul
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from engine import ScrabbleEngine, LETTER_SCORES
from utils import load_dictionary, group_by_length, validate_rack

# ANSI color codes
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

SCORE_DISPLAY = {c.upper(): v for c, v in LETTER_SCORES.items()}

BANNER = f"""{CYAN}{BOLD}
  +--------------------------------------------------+
  |   ____   ___  ____      _    ____  ____  _      |
  |  / ___| / __||  _ \\    / \\  | __ )| __ )| |     |
  |  \\___ \\| |   | |_) |  / _ \\ |  _ \\|  _ \\| |     |
  |   ___) | |__ |  _ <  / ___ \\| |_) | |_) | |___  |
  |  |____/ \\___||_| \\_\\/_/   \\_\\____/|____/|_____| |
  |                          SCRABBLE-X  v2.0        |
  +--------------------------------------------------+
{RESET}{DIM}  Word Finder | Scoring | Blank Tile ('?') Support{RESET}
"""


def print_score_chart():
    """Tampilkan tabel nilai huruf."""
    print(f"\n{DIM}  Nilai Huruf:{RESET}")
    entries = [f"{c}={v}" for c, v in sorted(SCORE_DISPLAY.items()) if c != '?']
    for i in range(0, len(entries), 9):
        print(f"  {DIM}{' | '.join(entries[i:i+9])}{RESET}")
    print(f"  {DIM}? = 0 (blank tile / wildcard){RESET}")


def render_word_item(item: dict) -> str:
    """Format satu kata dengan skor."""
    word  = item['word'].upper()
    score = item['score']
    blank = f" {DIM}[blank]{RESET}" if item['uses_blank'] else ""
    return f"{BOLD}{word}{RESET}{blank} {DIM}({score}pts){RESET}"


def main():
    print(BANNER)

    # --- Load kamus ---
    engine = ScrabbleEngine()
    print(f"  {DIM}Memuat kamus...{RESET}", end='\r')
    try:
        count = load_dictionary(engine)
        print(f"  {GREEN}[OK] Kamus dimuat: {count:,} kata{RESET}             ")
    except FileNotFoundError as e:
        print(f"\n  {RED}[ERROR] {e}{RESET}\n")
        return

    print()

    while True:
        # --- Input ---
        try:
            rack = input(f"  {CYAN}[?] Masukkan tile kamu (atau 'q' untuk keluar): {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {YELLOW}Sampai jumpa!{RESET}\n")
            break

        if rack.lower() in ('q', 'quit', 'exit'):
            print(f"\n  {YELLOW}Sampai jumpa!{RESET}\n")
            break

        # --- Validasi ---
        is_valid, error_msg = validate_rack(rack)
        if not is_valid:
            print(f"  {RED}[!] {error_msg}{RESET}\n")
            continue

        # --- Cari kata ---
        try:
            results = engine.find_all_words(rack)
        except ValueError as e:
            print(f"  {RED}[!] {e}{RESET}\n")
            continue

        if not results:
            print(f"  {YELLOW}[!] Tidak ada kata yang ditemukan untuk tile '{rack.upper()}'{RESET}\n")
            continue

        grouped = group_by_length(results)
        total   = len(results)
        best    = results[0]

        print(f"\n  {GREEN}[OK] Ditemukan {total} kata dari tile '{rack.upper()}'{RESET}")
        print(f"  {YELLOW}[*] Kata terbaik: {render_word_item(best)}{RESET}")

        # --- Tampilkan per grup panjang ---
        for length in sorted(grouped.keys()):
            words_in_group = grouped[length]

            if length == 7:
                label = f"{BOLD}{YELLOW}*** BINGO! 7 Huruf ***{RESET}"
            elif length == 6:
                label = f"{CYAN}6 Huruf{RESET}"
            else:
                label = f"{DIM}{length} Huruf{RESET}"

            sep = '-' * 28
            print(f"\n  --- {label} {sep}")

            word_strs = [render_word_item(w) for w in words_in_group]
            line = []
            for ws in word_strs:
                line.append(ws)
                if len(line) == 5:
                    print("  " + "  |  ".join(line))
                    line = []
            if line:
                print("  " + "  |  ".join(line))

        print()
        print_score_chart()
        print()


if __name__ == "__main__":
    main()