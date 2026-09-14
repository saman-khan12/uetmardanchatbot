# UET Mardan Assistant

A small RAG chatbot over uetmardan.edu.pk content, rebuilt clean.

## What changed from the previous version

- **One scraper, one crawl.** `scraper.py` replaces `scrape.py` +
  `scrape_pdfs.py`. The old pair crawled the whole site twice (once for
  page text, once just to find PDF links); this version does it once and
  saves both page text and PDF text into `data/raw/` with a single
  `manifest.json`.
- **No keyword-routing.** The old `chat.py`/`app.py` had a large, duplicated
  set of keyword tuples (`FEE_TERMS`, `DEPARTMENT_LIST_TERMS`, etc.) that
  special-cased how certain questions were answered, and the two files had
  already drifted out of sync with each other. `rag.py` now has one path:
  semantic search, every time.
- **`facts.py`** holds the handful of facts that must always be exact (fee
  amounts, bank account, entrance test body, VC name). It's included in
  every prompt as "verified facts," so the model prefers it over anything
  stale or ambiguous it retrieved — without needing per-question Python
  branches. One file to edit when something changes, instead of hunting
  through two apps' worth of keyword tuples.
- **`rag.py`** is the single place the retrieval + generation logic lives.
  Both `server.py` (web) and `cli.py` (terminal) import from it, so there's
  one implementation instead of two that can disagree.
- **No Streamlit.** `server.py` is a small Flask API; the UI is plain
  HTML/CSS/JS in `templates/` and `static/` — no framework, no build step,
  no rerun-on-every-keystroke behavior to fight.

## Project layout

```
uetbot/
  scraper.py         # crawl uetmardan.edu.pk -> data/raw/*.txt, data/pdfs/*.pdf
  build_index.py      # data/raw/*.txt -> chroma_db/ (embeddings index)
  facts.py             # small block of must-be-exact facts
  rag.py               # retrieval + Gemini generation (used by server.py and cli.py)
  server.py             # Flask API + serves the UI
  cli.py                 # terminal chat, same logic as the web UI
  templates/index.html
  static/style.css
  static/chat.js
  requirements.txt
  .env.example
```

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your `.env`**

   ```bash
   cp .env.example .env
   # then edit .env and paste in a fresh GOOGLE_API_KEY
   ```

   Note: rotate the API key that was in your old `_env` file — it was
   exposed in plaintext. Generate a new one in Google AI Studio / Cloud
   Console and use that instead.

3. **Scrape the site**

   ```bash
   python scraper.py
   ```

   This has to run somewhere with network access to uetmardan.edu.pk — I
   can't reach that domain from this sandbox, so I wasn't able to run or
   test this step myself. It's a straightforward `requests` +
   `BeautifulSoup` crawl, same approach as your original scripts, just
   merged into one pass.

4. **Build the index**

   ```bash
   python build_index.py
   ```

5. **Check `facts.py`** — update anything that's changed since the old
   hardcoded responses were written (the VC name especially, since
   leadership changes over time and I couldn't re-verify it here).

6. **Run it**

   ```bash
   python server.py
   ```

   Open http://127.0.0.1:5000. Or, for a terminal chat instead of the web
   UI: `python cli.py`.

## What I didn't change

Same retrieval stack as before (Chroma + `all-MiniLM-L6-v2` embeddings,
Gemini for generation) — you didn't ask to swap those out, and they're
reasonable choices for a site this size. If retrieval quality turns out to
be the actual pain point (rather than the routing code), the next thing
worth trying is usually better chunking (e.g. keeping each page section
intact instead of splitting mid-paragraph) before reaching for a bigger
embedding model.