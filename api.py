from fastapi import FastAPI
from engine import ScrabbleEngine
import uvicorn

app = FastAPI(title="Scrabble Api")
engine = ScrabbleEngine()

def startup():
    with open('data/dictionary.txt', 'r', encoding='utf-8') as f:
        for line in f:
            engine.insert(line.strip())

startup()

@app.get("/")
def home():
    return {"status": "Mesin aktif dan siap digunakan."}

@app.get("/solve/{tiles}")
def solve(tiles: str):
    results = engine.find_all_words(tiles)
    
    grouped_results = {}
    for word in results:
        length = len(word)
        if length >= 2:
            if length not in grouped_results:
                grouped_results[length] = []
            grouped_results[length].append(word)
            
    return {
        "tiles_input": tiles,
        "total_words_found": len(results),
        "grouped_words": grouped_results
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)