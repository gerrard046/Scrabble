# 🎯 Scrabble-X

**Word Finder berbasis Trie + Backtracking untuk Scrabble**

Cari semua kata valid dari tile Scrabble kamu, lengkap dengan **skor poin** setiap kata.

---

## ✨ Fitur

- 🔍 **Pencarian cepat** via Trie + Backtracking
- 🏆 **Sistem skor** — nilai tiap huruf sesuai standar Scrabble
- ❓ **Blank tile** — gunakan `?` sebagai wildcard (nilai 0 poin)
- 📦 **Grouped by length** — hasil dikelompokkan dari pendek ke Bingo (7 huruf)
- 🌐 **REST API** — endpoint FastAPI yang async dan proper
- 🖥️ **CLI interaktif** — tampilan berwarna dengan loop REPL
- 🎨 **Web UI** — antarmuka web modern Vanilla JS (Glassmorphism)

---

## 🚀 Cara Pakai

### Install dependensi
```bash
pip install -r requirements.txt
```

### Mode CLI
```bash
python main.py
```
Contoh input: `AEINRST` atau `AEIN??T` (dengan blank tile)

### Mode API
```bash
python api.py
```
Atau dengan uvicorn langsung:
```bash
uvicorn api:app --reload
```
Buka Swagger UI: http://127.0.0.1:8000/docs

### Mode Web UI
Pastikan API sudah berjalan. Buka file `frontend/index.html` di browser atau serve dengan HTTP server:
```bash
python -m http.server 3000
```
Lalu buka http://localhost:3000 (Pastikan `API_BASE` pada `frontend/app.js` sudah sesuai dengan alamat API Anda).

---

## 📡 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/` | Status API & info |
| GET | `/solve/{tiles}` | Cari kata dari tile |
| GET | `/score/{word}` | Hitung skor sebuah kata |
| GET | `/letter-values` | Lihat nilai tiap huruf |

### Query params `/solve/{tiles}`

| Param | Default | Keterangan |
|-------|---------|------------|
| `min_length` | 2 | Panjang minimum kata |
| `sort_by` | score | Urutan: `score`, `length`, `alpha` |
| `grouped` | true | Kelompokkan per panjang kata |

### Contoh
```
GET /solve/AEINRST
GET /solve/QUARTZ?min_length=4&sort_by=score
GET /score/QUARTZ
```

---

## 📊 Nilai Huruf Scrabble

| Poin | Huruf |
|------|-------|
| 1    | A, E, I, O, U, L, N, S, T, R |
| 2    | D, G |
| 3    | B, C, M, P |
| 4    | F, H, V, W, Y |
| 5    | K |
| 8    | J, X |
| 10   | Q, Z |
| 0    | ? (blank tile) |

---

## 📁 Struktur Proyek

```
SCRABBLEVIBECODING/
├── engine.py        # Core: Trie + Backtracking + Scoring
├── utils.py         # Shared helpers (load dict, group, validate)
├── main.py          # CLI interaktif
├── api.py           # FastAPI REST API
├── requirements.txt
├── frontend/        # Web UI (HTML/CSS/JS)
├── data/
│   └── dictionary.txt
└── README.md
```
