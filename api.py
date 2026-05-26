# ============================================================
#  SCRABBLE-X API v2.0
#  FastAPI backend - async, lifespan, proper error handling
# ============================================================
import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from engine import ScrabbleEngine, LETTER_SCORES
from utils import load_dictionary, group_by_length, validate_rack

# --- State global engine ---
engine = ScrabbleEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle handler — load kamus saat startup, cleanup saat shutdown."""
    print("[*] Memuat kamus Scrabble...")
    try:
        count = load_dictionary(engine)
        print(f"[OK] Kamus dimuat: {count:,} kata siap digunakan.")
    except FileNotFoundError as e:
        print(f"[!] PERINGATAN: {e}")
        print("[!] API akan berjalan tapi endpoint /solve tidak akan menemukan kata.")
    yield
    print("[*] Scrabble-X API shutdown.")


# --- Inisialisasi App ---
app = FastAPI(
    title="Scrabble-X API",
    description=(
        "🎯 **Scrabble Word Finder API** — Cari kata dari tile Scrabble kamu.\n\n"
        "Gunakan `?` sebagai blank tile (wildcard, nilai = 0 poin).\n\n"
        "Semua kata diurutkan berdasarkan skor tertinggi secara default."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — biar bisa diakses dari frontend / browser langsung
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Static frontend files
FRONTEND_DIR = Path(__file__).parent / "frontend"


# ============================================================
#  Endpoints
# ============================================================

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/solve/{tiles}", summary="Cari kata dari tile")
async def solve(
    tiles: str,
    min_length: int = Query(default=2, ge=2, le=7, description="Panjang minimum kata"),
    sort_by: str    = Query(default="score", pattern="^(score|length|alpha)$",
                            description="Urutan hasil: 'score', 'length', atau 'alpha'"),
    grouped: bool   = Query(default=True, description="Kelompokkan hasil berdasarkan panjang kata"),
):
    """
    Cari semua kata valid dari tile yang diberikan.

    - **tiles**: Huruf-huruf tile kamu (max 7). Gunakan `?` untuk blank tile.
    - **min_length**: Panjang minimum kata yang dicari (default 2).
    - **sort_by**: Urutan hasil — `score` (default), `length`, atau `alpha`.
    - **grouped**: Jika `true`, hasil dikelompokkan per panjang kata.
    """
    # --- Validasi ---
    is_valid, error_msg = validate_rack(tiles)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error_msg)

    # --- Cari kata ---
    try:
        results = engine.find_all_words(tiles, min_length=min_length)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # --- Sorting tambahan ---
    if sort_by == "length":
        results = sorted(results, key=lambda x: (-x['length'], -x['score']))
    elif sort_by == "alpha":
        results = sorted(results, key=lambda x: x['word'])
    # sort_by == "score" sudah default dari engine

    # --- Response ---
    response = {
        "tiles_input":       tiles.upper(),
        "total_words_found": len(results),
        "sort_by":           sort_by,
        "min_length":        min_length,
    }

    if grouped:
        grp = group_by_length(results)
        response["grouped_words"] = {
            str(k): v for k, v in sorted(grp.items())
        }
        response["best_word"] = results[0] if results else None
    else:
        response["words"] = results

    return response


@app.get("/score/{word}", summary="Hitung skor sebuah kata")
async def score_word(word: str):
    """
    Hitung nilai skor Scrabble dari sebuah kata (tanpa bonus papan).
    Kata tidak harus ada di kamus — hanya hitung nilai hurufnya.
    """
    word_clean = word.strip().lower()
    if not word_clean.isalpha():
        raise HTTPException(status_code=422, detail="Hanya huruf alfabet yang diterima.")

    breakdown = {
        char.upper(): LETTER_SCORES.get(char, 0)
        for char in word_clean
    }
    total = sum(breakdown.values())

    return {
        "word":       word.upper(),
        "total_score": total,
        "breakdown":  breakdown,
    }


@app.get("/letter-values", summary="Nilai huruf Scrabble")
async def letter_values():
    """Tampilkan nilai poin untuk setiap huruf dalam Scrabble."""
    return {
        "letter_scores": {k.upper(): v for k, v in LETTER_SCORES.items()},
        "note": "Blank tile (?) bernilai 0 poin tapi bisa menggantikan huruf apapun."
    }


# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)