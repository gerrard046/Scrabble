from engine import ScrabbleEngine

def load_dictionary(engine):
    # Memuat kamus
    with open('data/dictionary.txt', 'r', encoding='utf-8') as f:
        for line in f:
            engine.insert(line.strip())

def main():
    engine = ScrabbleEngine()
    load_dictionary(engine)
    print("--- [ SCRABBLE-X v1.0 ] ---")
    rack = input("[?] Enter your tiles: ")
    results = engine.find_all_words(rack)
    
    # Mengelompokkan kata berdasarkan panjangnya
    grouped_results = {}
    for word in results:
        length = len(word)
        if length >= 2: # Kata Scrabble minimal 2 huruf
            if length not in grouped_results:
                grouped_results[length] = []
            grouped_results[length].append(word.upper())
            
    print(f"\n[*] Found {len(results)} words:")
    
    # Menampilkan dari yang terkecil sampai Bingo
    for length in sorted(grouped_results.keys()):
        if length == 7:
            label = "BINGO! (7 Letters)"
        else:
            label = f"{length} Letters"
            
        print(f"\n--- {label} ---")
        # Menggabungkan kata dengan koma biar rapi
        print(", ".join(grouped_results[length]))

if __name__ == "__main__":
    main()