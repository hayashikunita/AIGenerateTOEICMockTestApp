# AIgenerateTOEICMockTestApp

<div>
<video controls src="https://github.com/user-attachments/assets/5c10b448-3441-486f-b1ce-4c49fb58c79e" muted="false"></video>
</div>

TOEIC-style Reading practice (Parts 5–7), one original question at a time — built to make your practice shine. No copyrighted test content is included; all items are generated templates or LLM-produced under guidance.

This repo now defaults to a Streamlit app (`streamlit_app.py`) with a Local generator and an optional OpenAI mode. The UI language is English throughout to support English-only practice and help your focus shine.

## Features (Streamlit) ✨

Focused, reliable features to help your daily drills shine:

- One-question-at-a-time generation for Parts 5, 6, and 7
- Engine: Local (built-in) or OpenAI (optional)
- Controls: Part, Difficulty (easy/medium/hard), Genre (Internal Notice, Press Release, etc.), Domain Vocabulary (IT, Manufacturing, etc.), Part 7 Length (short/medium/long)
- Actions: Submit / Restart / Next — fast cycles that let deliberate practice shine
- Downloads: current question (JSON/CSV) and ALL history (JSON/CSV) — also duplicated in the sidebar for quick access
- Visuals: Part 6 blanks are highlighted; adjustable font size (%) to make readability shine
- Robust option labeling (A–D) and answer normalization
- Autosave to disk (JSONL/CSV), import history, review past items, and a simple dashboard (accuracy/distribution) that lets your progress shine
- Randomize parameters option (Part/Difficulty/Genre/Domain/Length) per generation so variety can shine

Notes:
- Theme toggle has been removed; the app uses Streamlit’s default theme — clean defaults that let content shine.
- The Local engine does not require any API keys.

## Quick Start (Windows + PowerShell)

We recommend a Python virtual environment. In a few commands, you're ready to shine.

```powershell
# Create and activate venv
python -m venv .venv
./.venv/Scripts/Activate.ps1

# Install dependencies
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install streamlit openai packaging pandas

# (Optional) If you plan to use the OpenAI engine
$env:OPENAI_API_KEY = "sk-..."

# Run
./.venv/Scripts/python.exe -m streamlit run streamlit_app.py
```

Open the URL shown in the terminal (commonly http://localhost:8501).

If you prefer using a `.env` file for your API key, create `.env` in the project root:

```
OPENAI_API_KEY=sk-...
```

The app will load `.env` automatically if the environment variable is not already set.
Start a session and let your reading practice shine.

## How to Use

In the sidebar (tune your setup to shine):
- Engine: Local or OpenAI (ChatGPT)
- Section (Part): 5 / 6 / 7
- Difficulty: easy / medium / hard
- Genre: Internal Notice, Advertisement, Review, FAQ, Timetable/Schedule, Press Release, Policy, Invoice/Payment, Menu, Event, Weather Alert, Job Posting, Parking Rates, Social Post, Interview Schedule, Newsletter, Manual/Instructions, Recall Notice, Minutes, Survey
- Domain Vocabulary: IT, Manufacturing, Logistics, Medical, Finance, HR, Marketing, Education, Hospitality, Retail, Real Estate, Energy, Legal, Public, Aviation/Travel, Food Service, Construction, E-commerce, Support
- Model Preset (OpenAI): e.g., gpt-4o, gpt-4o-mini, o3-mini (key required) — choose what makes your speed/quality tradeoff shine
- Part 7 Passage Length: short / medium / long
- Randomize parameters: when enabled, each generation randomly picks Part/Difficulty/Genre/Domain/Length
- Autosave history to disk: appends every generated item to `data/history-YYYYMMDD.jsonl` and `.csv`
- Import history: by date (from autosave folder) or via upload
- Downloads (sidebar copy): Current Question (JSON/CSV) and ALL (JSON/CSV) so export workflows shine
- Font Size (%): adjust overall font size

Main area:
- Shows the current question with context (Part 6 text / Part 7 passage) and options A–D
- Buttons: Submit / Restart / Next (always shown on one row)
- A progress indicator (“Generating a question…”) appears during generation so the process shines clearly
- Current question downloads and ALL history downloads are at the top of the results area
- History (All): view count, clear history, load an item back into the quiz — make review sessions shine
- Dashboard: overall accuracy and distribution by Part/Genre; recent table (uses pandas if available)

## Data formats

Compact, portable schemas that make integrations shine.

Single question (download JSON):
```
{
  "part": 7,
  "partName": "Reading Comprehension",
  "stem": "...",
  "options": [{"letter":"A","text":"..."}, ...],
  "answer": "B",
  "explanationJa": "...",
  "context": { "passage": "..." }
}
```

ALL history (download JSON): an array of items with metadata used for analysis and exports. CSV exports include the same fields flattened into columns.

Autosave files (JSONL/CSV) are rotated daily by date. Fields include:
- timestamp, engine, model, p7_length, difficulty, genre, genreLabel, domain, domainLabel
- part, partName, stem, optionA, optionB, optionC, optionD, answer, explanationJa
- (may include groupId/blankIndex/blankCount for linkage; these are harmless if unused)

## OpenAI mode

- Uses the OpenAI Python SDK (v1+ supported) and attempts JSON-mode first, falling back to text parsing if needed — this helps structured outputs shine.
- Provide `OPENAI_API_KEY` via environment or `.env`.
- Model presets are selectable in the sidebar; you can switch based on availability/permissions.

## Local generator (no API)

See `toeic_generator.py`. It generates original items across Parts 5–7, designed to make signal words and grammar points shine:
- Part 5: many grammar/usage patterns (prepositions, verb forms, conjunctions, subjunctive, collocations, etc.)
- Part 6: various short document types (memo/notice/email/press release, etc.) with a single blank
- Part 7: short/medium/long passages; short items are biased by genre when selected

You can also use it directly in code:

```python
from toeic_generator import generate_dataset

data = generate_dataset(per_part=1, parts=[5,6,7], seed=123, p7_length="medium")
print([p["part"] for p in data.get("parts", [])])
```

## Troubleshooting

If something doesn’t shine as expected, try these tips:

- No spinner? The app uses a visible placeholder message (“Generating a question…”) instead of a transient spinner; it should appear reliably. If you still don’t see it, try a hard reload (Ctrl+F5) or widen the browser.
- Buttons wrapped into two lines? We force a single-row layout, but on extremely narrow viewports the framework may still wrap. Widening the window usually fixes this.
- Missing packages? Install `streamlit`, `openai`, `packaging`, and `pandas` (optional but recommended for the dashboard).
- OpenAI errors? Double-check your key and model access permissions, or switch models.

Still not shining? Open an issue and we’ll help.

## License and Content Policy

- All questions are original and TOEIC-like. We do not include or reproduce official/commercial questions.
- TOEIC is a registered trademark of ETS. This project is not affiliated with or endorsed by ETS.

---

Issues and PRs are welcome. If you need different exports (e.g., Anki/Quizlet) or additional analytics, we’re happy to help your study workflow shine—feel free to open a request.
