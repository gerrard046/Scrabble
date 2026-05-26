/* ================================================================
   SCRABBLE-X — app.js
   Vanilla JS, no dependencies
   ================================================================ */

const API_BASE = 'http://127.0.0.1:8000';

const LETTER_SCORES = {
  A:1,B:3,C:3,D:2,E:1,F:4,G:2,H:4,I:1,J:8,K:5,L:1,
  M:3,N:1,O:1,P:3,Q:10,R:1,S:1,T:1,U:1,V:4,W:4,X:8,Y:4,Z:10
};

// ── DOM refs ──────────────────────────────────────────────────────
const rackInput      = document.getElementById('rackInput');
const inputCounter   = document.getElementById('inputCounter');
const tileDisplay    = document.getElementById('tileDisplay');
const btnSolve       = document.getElementById('btnSolve');
const btnClear       = document.getElementById('btnClear');
const errorMsg       = document.getElementById('errorMsg');
const loading        = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const groupsContainer= document.getElementById('groupsContainer');
const statTotal      = document.getElementById('statTotal');
const statBest       = document.getElementById('statBest');
const statBestScore  = document.getElementById('statBestScore');
const statBingo      = document.getElementById('statBingo');
const minLenSel      = document.getElementById('minLen');
const sortBySel      = document.getElementById('sortBy');
const scoreGrid      = document.getElementById('scoreGrid');

// ── Score reference ───────────────────────────────────────────────
function buildScoreGrid() {
  const groups = {};
  for (const [letter, score] of Object.entries(LETTER_SCORES)) {
    if (!groups[score]) groups[score] = [];
    groups[score].push(letter);
  }
  const sorted = Object.entries(groups).sort((a,b) => a[0]-b[0]);
  for (const [score, letters] of sorted) {
    for (const letter of letters.sort()) {
      const el = document.createElement('div');
      el.className = 'score-item';
      el.innerHTML = `<span class="score-item-letter">${letter}</span><span class="score-item-val">=${score}</span>`;
      scoreGrid.appendChild(el);
    }
  }
  // blank tile
  const blank = document.createElement('div');
  blank.className = 'score-item';
  blank.innerHTML = `<span class="score-item-letter">?</span><span class="score-item-val">=0</span>`;
  scoreGrid.appendChild(blank);
}

// ── Tile Preview ──────────────────────────────────────────────────
function updateTilePreview(value) {
  const val = value.toUpperCase();
  const len = val.length;

  // Counter
  inputCounter.textContent = `${len} / 7`;
  inputCounter.className = 'input-counter' + (len === 7 ? ' full' : len >= 5 ? ' warn' : '');

  if (len === 0) {
    tileDisplay.innerHTML = '<span class="tile-hint">Ketik tile di bawah...</span>';
    return;
  }

  tileDisplay.innerHTML = '';
  for (const ch of val) {
    const tile = document.createElement('div');
    if (ch === '?') {
      tile.className = 'tile-char tile-char--blank';
      tile.textContent = '?';
    } else {
      tile.className = 'tile-char';
      const score = LETTER_SCORES[ch] || 0;
      tile.innerHTML = `${ch}<span class="tile-val">${score}</span>`;
    }
    tileDisplay.appendChild(tile);
  }
}

// ── Helpers ───────────────────────────────────────────────────────
function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.hidden = false;
}
function hideError() { errorMsg.hidden = true; }

function setLoading(on) {
  loading.hidden  = !on;
  btnSolve.disabled = on;
  if (on) resultsSection.hidden = true;
}

function scoreClass(score) {
  if (score <= 5)  return 'score-low';
  if (score <= 10) return 'score-mid';
  if (score <= 18) return 'score-high';
  return 'score-epic';
}

// Animate a number counting up
function animateNum(el, target, duration = 600) {
  const start = performance.now();
  const from  = parseInt(el.textContent) || 0;
  function step(ts) {
    const p = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(from + (target - from) * ease);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ── Render results ────────────────────────────────────────────────
function renderResults(data) {
  const { total_words_found, best_word, grouped_words } = data;

  // Stats
  animateNum(statTotal, total_words_found);
  statBest.textContent      = best_word ? best_word.word.toUpperCase() : '-';
  animateNum(statBestScore, best_word ? best_word.score : 0);
  const bingoGroup = grouped_words['7'] || [];
  animateNum(statBingo, bingoGroup.length);

  // Groups
  groupsContainer.innerHTML = '';
  const lengths = Object.keys(grouped_words).map(Number).sort((a,b)=>a-b);

  lengths.forEach((len, idx) => {
    const words   = grouped_words[String(len)];
    const isBingo = len === 7;

    const group = document.createElement('div');
    group.className = `word-group${isBingo ? ' bingo' : ''}`;
    group.dataset.len = len;
    group.style.animationDelay = `${idx * 0.06}s`;

    const label = isBingo ? '🎉 BINGO! 7 Huruf' : `${len} Huruf`;
    const badgeLabel = isBingo ? '7' : len;

    group.innerHTML = `
      <div class="group-header">
        <div class="group-header-left">
          <span class="group-badge">${badgeLabel}</span>
          <span class="group-title">${isBingo ? '<span class="bingo-star">⭐</span> BINGO! — 7 Huruf' : `${len} Huruf`}</span>
          <span class="group-count">${words.length} kata</span>
        </div>
        <span class="group-chevron">▶</span>
      </div>
      <div class="group-body"></div>
    `;

    const body = group.querySelector('.group-body');
    words.forEach((item, wi) => {
      const chip = document.createElement('div');
      chip.className = `word-chip ${scoreClass(item.score)}${item.uses_blank ? ' word-chip--blank' : ''}`;
      chip.style.animationDelay = `${wi * 0.015}s`;
      chip.title = item.uses_blank ? `${item.word.toUpperCase()} (menggunakan blank tile)` : item.word.toUpperCase();
      chip.innerHTML = `
        ${item.word.toUpperCase()}
        <span class="chip-score">${item.score}pts</span>
      `;
      body.appendChild(chip);
    });

    // Toggle open/close
    const header = group.querySelector('.group-header');
    header.addEventListener('click', () => {
      group.classList.toggle('open');
    });

    groupsContainer.appendChild(group);

    // Auto-open BINGO and the highest-score group
    if (isBingo || idx === lengths.length - 1) {
      requestAnimationFrame(() => group.classList.add('open'));
    }
  });

  resultsSection.hidden = false;
}

// ── Solve ─────────────────────────────────────────────────────────
async function solve() {
  hideError();
  const rack   = rackInput.value.trim();
  const minLen = minLenSel.value;
  const sortBy = sortBySel.value;

  if (!rack) { showError('Masukkan tile dulu bro!'); return; }
  if (rack.length > 7) { showError('Maksimal 7 tile dalam Scrabble!'); return; }

  const valid = /^[a-zA-Z?]+$/.test(rack);
  if (!valid) { showError('Hanya huruf A-Z dan ? (blank tile) yang diperbolehkan.'); return; }

  setLoading(true);

  try {
    const url  = `${API_BASE}/solve/${encodeURIComponent(rack.toUpperCase())}?min_length=${minLen}&sort_by=${sortBy}&grouped=true`;
    const resp = await fetch(url);

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }

    const data = await resp.json();

    if (data.total_words_found === 0) {
      showError(`Tidak ada kata ditemukan untuk tile "${rack.toUpperCase()}". Coba tile yang berbeda!`);
    } else {
      renderResults(data);
    }

  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      showError('Tidak bisa terhubung ke API. Pastikan server berjalan di localhost:8000');
    } else {
      showError(`Error: ${err.message}`);
    }
  } finally {
    setLoading(false);
  }
}

// ── Event listeners ───────────────────────────────────────────────
rackInput.addEventListener('input', () => {
  // Force uppercase & filter invalid chars
  const raw     = rackInput.value;
  const cleaned = raw.toUpperCase().replace(/[^A-Z?]/g, '').slice(0, 7);
  if (cleaned !== raw.toUpperCase()) rackInput.value = cleaned;
  updateTilePreview(cleaned);
  hideError();
});

rackInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') solve();
});

btnSolve.addEventListener('click', solve);

btnClear.addEventListener('click', () => {
  rackInput.value = '';
  updateTilePreview('');
  hideError();
  resultsSection.hidden = true;
  groupsContainer.innerHTML = '';
  rackInput.focus();
});

// ── Init ──────────────────────────────────────────────────────────
buildScoreGrid();
rackInput.focus();

// Demo: pre-fill with a fun word on load
window.addEventListener('DOMContentLoaded', () => {
  // Small delay so tile animation looks cool
  setTimeout(() => {
    rackInput.value = '';
    updateTilePreview('');
  }, 300);
});
