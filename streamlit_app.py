from __future__ import annotations

from typing import Any, Dict, List, Optional
import re
import io
import csv
import json
import random
import time
import datetime as dt
from pathlib import Path
import os

import streamlit as st

from toeic_generator import generate_dataset

# Optional: OpenAI path
try:
    from llm_generator import generate_dataset_openai  # type: ignore
    HAS_LLM = True
except Exception:
    HAS_LLM = False


def filter_reading_only(data: Dict[str, Any]) -> Dict[str, Any]:
    parts = [p for p in data.get("parts", []) if int(p.get("part", 0)) >= 5]
    data = dict(data)
    data["parts"] = parts
    return data


def collect_questions(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in data.get("parts", []):
        for q in p.get("questions", []):
            qc = dict(q)
            qc["_part"] = p.get("part")
            qc["_part_name"] = p.get("name")
            out.append(qc)
    return out

def derive_stem(q: Dict[str, Any]) -> str:
    ctx = q.get("context") or {}
    return (
        q.get("stem")
        or ctx.get("question")
        or ctx.get("imageDescription")
        or ctx.get("audioTranscript")
        or ctx.get("talk")
        or ctx.get("passage")
        or "Select the best answer"
    )


def option_to_letter(opt_text: str) -> Optional[str]:
    """Extract option letter (A-D) from various label styles like 'A.', 'A)', 'A:', 'A -'."""
    if not isinstance(opt_text, str):
        return None
    m = re.match(r"^\s*([A-Da-d])\s*[\.|\)|\:|\-]", opt_text)
    if m:
        return m.group(1).upper()
    # Strict 'A.' legacy
    if len(opt_text) >= 2 and opt_text[1] == ".":
        c = opt_text[0].upper()
        if c in ("A", "B", "C", "D"):
            return c
    return None


def strip_option_label(opt_text: str) -> str:
    """Remove leading label like 'A.', 'A)', 'A:' from option text, returning clean body."""
    if not isinstance(opt_text, str):
        return str(opt_text)
    m = re.match(r"^\s*[A-Da-d]\s*[\.|\)|\:|\-]\s*(.*)$", opt_text)
    if m:
        return m.group(1).strip()
    # Fallback: strip 'A. ' only
    if len(opt_text) >= 2 and opt_text[1] == ".":
        return opt_text[2:].strip()
    return opt_text.strip()


def normalize_answer_letter(ans: Optional[str]) -> Optional[str]:
    if not ans:
        return None
    if isinstance(ans, str):
        m = re.match(r"^\s*([A-Da-d])", ans)
        if m:
            return m.group(1).upper()
        up = ans.strip().upper()
        if up in ("A", "B", "C", "D"):
            return up
    return None


def _fallback_dataset(part: int = 5) -> Dict[str, Any]:
    if part not in (5, 6, 7):
        part = 5
    if part == 5:
        q = {
            "id": "FB-P5-Q1",
            "stem": "Please choose the best word: We will ______ the report by Friday.",
            "options": ["A. submit", "B. repair", "C. cancel", "D. extend"],
            "answer": "A",
            "explanationJa": "『金曜までに報告書を提出する』は submit the report が自然です。fallback表示です。",
        }
        name = "Incomplete Sentences"
    elif part == 6:
        q = {
            "id": "FB-P6-Q1",
            "context": {"text": "Reminder: The meeting will start at 10 a.m. Please 【_____】 on time."},
            "options": ["A. arrive", "B. arriving", "C. arrival", "D. arrived"],
            "answer": "A",
            "explanationJa": "Please の後ろは動詞の原形 arrive が適切です。fallback表示です。",
        }
        name = "Text Completion"
    else:  # part 7
        q = {
            "id": "FB-P7-Q1",
            "context": {"passage": "Notice: The cafe will close at 6 p.m. today for maintenance."},
            "stem": "Why will the cafe close early?",
            "options": [
                "A. For maintenance",
                "B. For a special event",
                "C. Due to a holiday",
                "D. Because of a staff meeting",
            ],
            "answer": "A",
            "explanationJa": "本文に maintenance（保守）のためと明記。fallback表示です。",
        }
        name = "Reading Comprehension"

    return {
        "title": "Fallback - Single Question",
        "version": "1.0.0",
        "language": "en",
        "explanationsLanguage": "ja",
        "createdAt": "",
        "parts": [
            {
                "part": part,
                "name": name,
                "instructions": "",
                "questions": [q],
            }
        ],
        "metadata": {"noteJa": "自動生成が失敗したための代替問題です。"},
    }


# ------------------------------ UI ------------------------------
# --- .env ロード（OPENAI_API_KEY など） ---
def _load_env_once() -> None:
    try:
        # 既に環境変数に存在する場合は上書きしない
        def _apply(path: Path) -> None:
            if not path.exists():
                return
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and (k not in os.environ or not os.environ.get(k)):
                    os.environ[k] = v
        here = Path(__file__).resolve().parent
        _apply(here / ".env")
        _apply(here.parent / ".env")  # 親にも置けるように
    except Exception:
        pass

_load_env_once()

st.set_page_config(page_title="TOEIC Mock (Reading) - Streamlit", layout="wide")
st.title("TOEIC Mock (Reading) - Streamlit")

# Randomize チェックの変更時に自動生成をトリガするためのフラグ設定
def _on_randomize_toggle() -> None:
    st.session_state._randomize_trigger = True

# Sidebar Controls
with st.sidebar:
    st.header("Controls")
    engine = st.selectbox("Engine", ["local", "openai"], format_func=lambda x: "Local Generator" if x == "local" else "OpenAI (ChatGPT)")
    section_value = st.selectbox("Section (Part)", [5, 6, 7], index=2)
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
    genre_options = [
            "Internal Notice","Advertisement","Review","FAQ","Timetable/Schedule",
            "Press Release","Policy","Invoice/Payment","Menu","Event",
            "Weather Alert","Job Posting","Parking Rates","Social Post","Interview Schedule",
            "Newsletter","Manual/Instructions","Recall Notice","Minutes","Survey",
        ]
    genre_label = st.selectbox("Genre", genre_options, index=0)
    domain_options = [
            "IT","Manufacturing","Logistics","Medical",
            "Finance","HR","Marketing","Education","Hospitality","Retail",
            "Real Estate","Energy","Legal","Public","Aviation/Travel",
            "Food Service","Construction","E-commerce","Support",
        ]
    domain_label = st.selectbox("Domain Vocabulary", domain_options, index=0)
    # Model preset + custom
    model_preset = st.selectbox("Model Preset (OpenAI)", [
        "gpt-4o","gpt-4o-mini","o3-mini","gpt-4.1","gpt-4.1-mini"
    ], index=0)
    p7_length = st.selectbox("P7 Passage Length", ["short", "medium", "long"], index=2)
    openai_key = ""
    if engine == "openai":
        # Secure input (leave blank to use .env/environment)
        openai_key = st.text_input("OpenAI API Key (leave blank to use .env/environment)", type="password", value="")
    st.markdown("---")
    autosave_enabled = st.checkbox("Autosave history to disk", value=False, help="Append each generated question to JSONL/CSV automatically.")
    autosave_dir = st.text_input("Autosave folder", value="data", help="Creates/appends history-YYYYMMDD.jsonl and .csv per day.")
    st.caption("Note: Write permission is required. On Windows, a folder under the project is recommended.")
    # Import on startup / on demand
    st.markdown("---")
    import_on_startup = st.checkbox("Load history on startup", value=False)
    import_date = st.date_input("History Date", value=dt.date.today())
    import_now = st.button("Import history now")
    uploaded_file = st.file_uploader("Import .jsonl or .csv", type=["jsonl","csv"], accept_multiple_files=False)
    st.markdown("---")
    randomize_params = st.checkbox(
        "Randomize parameters (Part/Difficulty/Genre/Domain/Length)",
        value=st.session_state.get("randomize_params", False),
        key="randomize_params",
        help="When enabled, each generation randomly picks Part, Difficulty, Genre, Domain, and Length.",
        on_change=_on_randomize_toggle,
    )
    st.markdown("---")
    # Sidebar Downloads (冗長だがメイン領域の代替として常時見える場所にも配置)
    st.subheader("Downloads")
    try:
        # 現在の問題（あれば）
        if st.session_state.get("dataset") and st.session_state.dataset.get("questions"):
            _q = st.session_state.dataset["questions"][0]
            _stem = derive_stem(_q)
            _opts = _q.get("options", [])
            _letters: List[str] = []
            _text_map: Dict[str, str] = {}
            for i, _opt in enumerate(_opts):
                _letter = option_to_letter(_opt) or chr(ord("A") + i)
                _text = strip_option_label(_opt)
                _letters.append(_letter)
                _text_map[_letter] = _text
            _export = {
                "part": _q.get("_part"),
                "partName": _q.get("_part_name"),
                "stem": _stem,
                "options": [{"letter": l, "text": _text_map.get(l, "")} for l in _letters],
                "answer": normalize_answer_letter(_q.get("answer")),
                "explanationJa": _q.get("explanationJa", ""),
                "context": _q.get("context") or {},
            }
            _json_bytes = json.dumps(_export, ensure_ascii=False, indent=2).encode("utf-8")
            _csv_buf = io.StringIO()
            _w = csv.writer(_csv_buf)
            _w.writerow(["part","partName","stem","optionA","optionB","optionC","optionD","answer","explanationJa"])
            _w.writerow([
                _export["part"], _export["partName"], _export["stem"],
                _text_map.get("A",""), _text_map.get("B",""), _text_map.get("C",""), _text_map.get("D",""),
                _export["answer"], _export["explanationJa"],
            ])
            _csv_bytes = _csv_buf.getvalue().encode("utf-8-sig")
            st.download_button("Download JSON", data=_json_bytes, file_name="toeic_question.json", mime="application/json", key="dl_sidebar_json")
            st.download_button("Download CSV", data=_csv_bytes, file_name="toeic_question.csv", mime="text/csv", key="dl_sidebar_csv")
        # 全履歴（あれば）
        _hist = st.session_state.get("history", [])
        if _hist:
            _all_json = json.dumps(_hist, ensure_ascii=False, indent=2).encode("utf-8")
            _buf = io.StringIO()
            _cw = csv.writer(_buf)
            _cw.writerow(["timestamp","engine","model","p7_length","difficulty","genre","genreLabel","domain","domainLabel",
                          "part","partName","stem","optionA","optionB","optionC","optionD","answer","explanationJa",
                          "groupId","blankIndex","blankCount"])
            for _item in _hist:
                _omap = {o.get("letter"): o.get("text") for o in _item.get("options", [])}
                _cw.writerow([
                    _item.get("timestamp",""), _item.get("engine",""), _item.get("model",""), _item.get("p7_length",""),
                    _item.get("difficulty",""), _item.get("genre",""), _item.get("genreLabel",""),
                    _item.get("domain",""), _item.get("domainLabel",""),
                    _item.get("part",""), _item.get("partName",""), _item.get("stem",""),
                    _omap.get("A",""), _omap.get("B",""), _omap.get("C",""), _omap.get("D",""),
                    _item.get("answer",""), _item.get("explanationJa",""),
                    _item.get("groupId",""), _item.get("blankIndex",""), _item.get("blankCount",""),
                ])
            _all_csv = _buf.getvalue().encode("utf-8-sig")
            st.download_button("Download ALL (JSON)", data=_all_json, file_name="toeic_questions_all.json", mime="application/json", key="dl_sidebar_all_json")
            st.download_button("Download ALL (CSV)", data=_all_csv, file_name="toeic_questions_all.csv", mime="text/csv", key="dl_sidebar_all_csv")
    except Exception as _e:
        st.caption(f"Failed to prepare downloads: {_e}")
    st.markdown("---")
    font_scale = st.slider("Font Size (%)", min_value=90, max_value=150, value=100, step=5)
    load_clicked = st.button("Load One Question")

# Apply font size via CSS only (Theme control removed; use Streamlit default theme)
css_font_slot = st.empty()
css_font_slot.markdown(
    f"""
<style>
html, body, [class^=\"css\"]  {{
    font-size: {font_scale}%;
}}
</style>
""",
    unsafe_allow_html=True,
)
    


def _do_generate(engine: str, part_num: int, seed_opt: Optional[int], p7_length: str, model_name: str, openai_key: str,
                 difficulty: Optional[str] = None, genre: Optional[str] = None, domain: Optional[str] = None):
    # Apply model preset override
    if engine == "openai":
        if model_preset and model_preset != "Custom":
            model_name = model_preset
    if engine == "openai":
        if not HAS_LLM:
            raise RuntimeError("llm_generator が見つかりません。OpenAI 生成には llm_generator.py と OPENAI_API_KEY が必要です。")
        data = generate_dataset_openai(
            title="TOEIC Mock - Single Question (LLM)",
            part=part_num,
            seed=seed_opt,
            p7_length=(p7_length or "long"),
            model=(model_name or "gpt-4o"),
            api_key=(openai_key or None),
            difficulty=difficulty,
            genre=genre,
            domain=domain,
        )
    else:
        data = generate_dataset(
            title="TOEIC Mock - Single Question",
            per_part=1,
            parts=[part_num],
            seed=seed_opt,
            p7_length=(p7_length or "long"),
            difficulty=difficulty,
            genre=genre,
            domain=domain,
        )
    return data


def _autosave_history_item(item: Dict[str, Any], enabled: bool, out_dir: str) -> None:
    if not enabled:
        return
    try:
        base = Path(out_dir).expanduser()
        base.mkdir(parents=True, exist_ok=True)
        date_str = dt.datetime.now().strftime("%Y%m%d")
        jsonl_path = base / f"history-{date_str}.jsonl"
        csv_path = base / f"history-{date_str}.csv"

        # JSONL: 1行1レコード
        with jsonl_path.open("a", encoding="utf-8") as jf:
            jf.write(json.dumps(item, ensure_ascii=False) + "\n")

        # CSV: ヘッダー有・1行追記
        header = [
            "timestamp","engine","model","p7_length","difficulty","genre","genreLabel","domain","domainLabel",
            "part","partName","stem","optionA","optionB","optionC","optionD","answer","explanationJa",
            "groupId","blankIndex","blankCount"
        ]
        row_map = {o.get("letter"): o.get("text") for o in item.get("options", [])}
        row = [
            item.get("timestamp",""), item.get("engine",""), item.get("model",""), item.get("p7_length",""),
            item.get("difficulty",""), item.get("genre",""), item.get("genreLabel",""),
            item.get("domain",""), item.get("domainLabel",""),
            item.get("part",""), item.get("partName",""), item.get("stem",""),
            row_map.get("A",""), row_map.get("B",""), row_map.get("C",""), row_map.get("D",""),
            item.get("answer",""), item.get("explanationJa",""),
            item.get("groupId",""), item.get("blankIndex",""), item.get("blankCount",""),
        ]
        csv_exists = csv_path.exists()
        with csv_path.open("a", encoding="utf-8-sig", newline="") as cf:
            w = csv.writer(cf)
            if not csv_exists:
                w.writerow(header)
            w.writerow(row)
    except Exception as e:
        # 書き込み失敗はアプリを止めずに通知のみ
        st.warning(f"Autosave 失敗: {e}")


def _parse_history_csv_row(header: List[str], row: List[str]) -> Dict[str, Any]:
    idx = {k: i for i, k in enumerate(header)}
    get = lambda k, default="": row[idx[k]] if k in idx and idx[k] < len(row) else default
    item: Dict[str, Any] = {
        "timestamp": get("timestamp"),
        "engine": get("engine"),
        "model": get("model"),
        "p7_length": get("p7_length"),
        "difficulty": get("difficulty"),
        "genre": get("genre"),
        "genreLabel": get("genreLabel"),
        "domain": get("domain"),
        "domainLabel": get("domainLabel"),
        "part": int(get("part","0") or 0),
        "partName": get("partName"),
        "stem": get("stem"),
        "options": [
            {"letter": "A", "text": get("optionA")},
            {"letter": "B", "text": get("optionB")},
            {"letter": "C", "text": get("optionC")},
            {"letter": "D", "text": get("optionD")},
        ],
        "answer": get("answer"),
        "explanationJa": get("explanationJa"),
        "context": {},
    }
    return item


def _import_history_file(path: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not path.exists():
        return items
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        items.append(obj)
                except Exception:
                    continue
    elif path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header:
                for row in reader:
                    try:
                        items.append(_parse_history_csv_row(header, row))
                    except Exception:
                        continue


def _maybe_import_on_startup(enabled: bool, base_dir: str, date_value: dt.date) -> None:
    if not enabled:
        return
    if st.session_state.get("_history_loaded_once"):
        return
    date_str = date_value.strftime("%Y%m%d")
    base = Path(base_dir)
    jsonl = base / f"history-{date_str}.jsonl"
    csvp = base / f"history-{date_str}.csv"
    items = _import_history_file(jsonl) if jsonl.exists() else _import_history_file(csvp)
    if items:
        _merge_history(items)
        st.session_state._history_loaded_once = True
        st.toast(f"Imported {len(items)} history items from {jsonl.name if jsonl.exists() else csvp.name}")


def _merge_history(items: List[Dict[str, Any]]) -> None:
    # simple dedupe based on (timestamp, stem, part)
    seen = set((x.get("timestamp", ""), x.get("stem", ""), x.get("part", "")) for x in st.session_state.history)
    for it in items:
        key = (it.get("timestamp", ""), it.get("stem", ""), it.get("part", ""))
        if key not in seen:
            st.session_state.history.append(it)
            seen.add(key)


# Initialize session state
if "dataset" not in st.session_state:
    st.session_state.dataset = None
if "state" not in st.session_state:
    st.session_state.state = {"index": 0, "score": 0, "answered": False}
if "history" not in st.session_state:
    # 生成した全問題の履歴（アプリ起動中のみ保持）
    st.session_state.history = []
if "_history_loaded_once" not in st.session_state:
    st.session_state._history_loaded_once = False

# Import on startup (if enabled)
_maybe_import_on_startup(import_on_startup, autosave_dir, import_date)

# Import now (button or file uploader)
if import_now:
    date_str = import_date.strftime("%Y%m%d")
    base = Path(autosave_dir)
    src = base / f"history-{date_str}.jsonl"
    if not src.exists():
        src = base / f"history-{date_str}.csv"
    items = _import_history_file(src)
    if items:
        _merge_history(items)
        st.success(f"Imported {len(items)} items from {src}")
    else:
        st.warning(f"No items found at {src}")
if uploaded_file is not None:
    # Save to a temp path in memory and parse
    suffix = ".jsonl" if uploaded_file.name.lower().endswith(".jsonl") else ".csv"
    content = uploaded_file.read().decode("utf-8-sig")
    items: List[Dict[str, Any]] = []
    if suffix == ".jsonl":
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    items.append(obj)
            except Exception:
                continue
    else:
        reader = csv.reader(io.StringIO(content))
        header = next(reader, None)
        if header:
            for row in reader:
                try:
                    items.append(_parse_history_csv_row(header, row))
                except Exception:
                    continue
    if items:
        _merge_history(items)
        st.success(f"Imported {len(items)} items from uploaded file: {uploaded_file.name}")

# Generate on click (sidebar Load) または Randomize 切替直後の自動生成
if load_clicked or st.session_state.get("_randomize_trigger"):
    _status = st.empty()
    _status.info("Generating a question…")
    try:
            # base params from UI
            part_num = int(section_value) if section_value in (5, 6, 7) else 7
            effective_difficulty = difficulty
            effective_genre_label = genre_label
            effective_domain_label = domain_label
            effective_p7_length = p7_length
            # randomize if enabled
            if randomize_params:
                part_num = random.choice([5, 6, 7])
                effective_difficulty = random.choice(["easy", "medium", "hard"])
                effective_genre_label = random.choice(genre_options)
                effective_domain_label = random.choice(domain_options)
                effective_p7_length = random.choice(["short", "medium", "long"])
            # Always use a fresh random seed per generation
            seed_opt = random.randint(1, 2**31 - 1)
            genre_map = {
                "Internal Notice": "notice",
                "Advertisement": "advertisement",
                "Review": "review",
                "FAQ": "faq",
                "Timetable/Schedule": "schedule",
                "Press Release": "press_release",
                "Policy": "policy",
                "Invoice/Payment": "invoice",
                "Menu": "menu",
                "Event": "event",
                "Weather Alert": "weather",
                "Job Posting": "job_posting",
                "Parking Rates": "parking",
                "Social Post": "social_post",
                "Interview Schedule": "interview",
                "Newsletter": "newsletter",
                "Manual/Instructions": "manual",
                "Recall Notice": "recall_notice",
                "Minutes": "minutes",
                "Survey": "survey",
            }
            domain_map = {
                "IT": "it",
                "Manufacturing": "manufacturing",
                "Logistics": "logistics",
                "Medical": "medical",
                "Finance": "finance",
                "HR": "hr",
                "Marketing": "marketing",
                "Education": "education",
                "Hospitality": "hospitality",
                "Retail": "retail",
                "Real Estate": "realestate",
                "Energy": "energy",
                "Legal": "legal",
                "Public": "public",
                "Aviation/Travel": "aviation",
                "Food Service": "food",
                "Construction": "construction",
                "E-commerce": "ecommerce",
                "Support": "support",
            }
            data = _do_generate(
                engine, part_num, seed_opt, effective_p7_length, model_preset, openai_key,
                difficulty=effective_difficulty,
                genre=genre_map.get(effective_genre_label),
                domain=domain_map.get(effective_domain_label),
            )
            data = filter_reading_only(data)
            questions = collect_questions(data)[:1]
            # 効果的パラメータをセッションに保存（連続空所の次の設問でも利用）
            st.session_state._effective_params = {
                "p7_length": effective_p7_length,
                "difficulty": effective_difficulty,
                "genreLabel": effective_genre_label,
                "genre": genre_map.get(effective_genre_label),
                "domainLabel": effective_domain_label,
                "domain": domain_map.get(effective_domain_label),
                "part": part_num,
            }
            if not questions:
                fb = _fallback_dataset(part_num)
                fb_q = collect_questions(fb)
                st.session_state.dataset = {"questions": fb_q}
                # 履歴に追記（フォールバック）
                q = fb_q[0]
                # options 整形
                letters: List[str] = []
                text_map: Dict[str, str] = {}
                for i, opt in enumerate(q.get("options", [])):
                    letter = option_to_letter(opt) or chr(ord("A") + i)
                    text = strip_option_label(opt)
                    letters.append(letter)
                    text_map[letter] = text
                ctx = q.get("context") or {}
                item = {
                    "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                    "engine": engine,
                    "model": model_preset,
                    "p7_length": effective_p7_length,
                    "difficulty": effective_difficulty,
                    "genreLabel": effective_genre_label,
                    "genre": genre_map.get(effective_genre_label),
                    "domainLabel": effective_domain_label,
                    "domain": domain_map.get(effective_domain_label),
                    "part": q.get("_part"),
                    "partName": q.get("_part_name"),
                    "stem": derive_stem(q),
                    "options": [{"letter": l, "text": text_map.get(l, "")} for l in letters],
                    "answer": normalize_answer_letter(q.get("answer")),
                    "explanationJa": q.get("explanationJa", ""),
                    "context": ctx,
                    "groupId": ctx.get("groupId"),
                    "blankIndex": ctx.get("blankIndex"),
                    "blankCount": ctx.get("blankCount"),
                }
                st.session_state.history.append(item)
                _autosave_history_item(item, autosave_enabled, autosave_dir)
            else:
                st.session_state.dataset = {"questions": questions}
                # 履歴に追記（通常）
                q = questions[0]
                letters: List[str] = []
                text_map: Dict[str, str] = {}
                for i, opt in enumerate(q.get("options", [])):
                    letter = option_to_letter(opt) or chr(ord("A") + i)
                    text = strip_option_label(opt)
                    letters.append(letter)
                    text_map[letter] = text
                ctx = q.get("context") or {}
                item = {
                    "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                    "engine": engine,
                    "model": model_preset,
                    "p7_length": effective_p7_length,
                    "difficulty": effective_difficulty,
                    "genreLabel": effective_genre_label,
                    "genre": genre_map.get(effective_genre_label),
                    "domainLabel": effective_domain_label,
                    "domain": domain_map.get(effective_domain_label),
                    "part": q.get("_part"),
                    "partName": q.get("_part_name"),
                    "stem": derive_stem(q),
                    "options": [{"letter": l, "text": text_map.get(l, "")} for l in letters],
                    "answer": normalize_answer_letter(q.get("answer")),
                    "explanationJa": q.get("explanationJa", ""),
                    "context": ctx,
                    "groupId": ctx.get("groupId"),
                    "blankIndex": ctx.get("blankIndex"),
                    "blankCount": ctx.get("blankCount"),
                }
                st.session_state.history.append(item)
                _autosave_history_item(item, autosave_enabled, autosave_dir)
            st.session_state.state = {"index": 0, "score": 0, "answered": False}
            _status.success("Generation completed.")
            time.sleep(0.3)
            _status.empty()
    except Exception as e:
        part_num = 7
        try:
            part_num = int(section_value) if section_value in (5, 6, 7) else 7
        except Exception:
            pass
        fb = _fallback_dataset(part_num)
        fb_q = collect_questions(fb)
        st.session_state.dataset = {"questions": fb_q}
        st.session_state.state = {"index": 0, "score": 0, "answered": False}
        _status.warning(f"Failed to generate. Showing fallback: {e}")
    # 一度だけのトリガにする
    if st.session_state.get("_randomize_trigger"):
        st.session_state._randomize_trigger = False

# Render Question
if not st.session_state.dataset or not st.session_state.dataset.get("questions"):
    st.info("Use the sidebar to set options and click 'Load One Question'.")
else:
    dataset = st.session_state.dataset
    state = st.session_state.state
    questions: List[Dict[str, Any]] = dataset["questions"]
    idx = max(0, min(int(state.get("index", 0)), len(questions) - 1))
    q = questions[idx]

    st.subheader(f"[{idx+1}/{len(questions)}] Part {q.get('_part')}: {q.get('_part_name')}")

    stem = derive_stem(q)
    st.write(stem)

    ctx_obj = q.get("context") or {}
    if isinstance(ctx_obj.get("conversation"), list):
        with st.expander("Conversation", expanded=True):
            for t in ctx_obj["conversation"]:
                st.write(f"{t.get('speaker','?')}: {t.get('text','')}")
    if ctx_obj.get("text"):
        # Highlight blanks for Part 6
        with st.expander("Text", expanded=True):
            txt = str(ctx_obj.get("text") or "")
            # 強調: 【_____】 あるいは [_____]
            def _hl_all(m: re.Match) -> str:
                return '<span style="background: #fff59d; color: #000; font-weight:700; padding:2px 4px; border-radius:3px;">' + m.group(0) + '</span>'
            if q.get("_part") == 6:
                # If numbered blanks exist (e.g., 【_____1】), highlight the current blank in green and others in yellow
                active_idx = ctx_obj.get("blankIndex", None)
                if isinstance(active_idx, int) and re.search(r"【_+\d+】", txt):
                    def _hl_num(m: re.Match) -> str:
                        num = int(m.group(1))
                        color = "#a5d6a7" if num == (active_idx + 1) else "#fff59d"
                        return f'<span style="background: {color}; color: #000; font-weight:700; padding:2px 4px; border-radius:3px;">' + m.group(0) + '</span>'
                    html_txt = re.sub(r"【_+(\d+)】", _hl_num, txt)
                else:
                    html_txt = re.sub(r"[【\[]_{3,}[】\]]|[【\[]+_{3,}[】\]]+|【_____】", _hl_all, txt)
                st.markdown(html_txt, unsafe_allow_html=True)
            else:
                st.write(txt)
    if ctx_obj.get("passage"):
        with st.expander("Passage", expanded=True):
            st.write(ctx_obj.get("passage"))

    # Build options as letter-based choices (A/B/C/D) with visible text
    opts = q.get("options", [])
    letters: List[str] = []
    text_map: Dict[str, str] = {}
    for i, opt in enumerate(opts):
        letter = option_to_letter(opt)
        text = strip_option_label(opt)
        if not letter:
            letter = chr(ord("A") + i)
        letters.append(letter)
        text_map[letter] = text

    choice = st.radio(
        "Choices",
        options=letters,
        format_func=lambda l: f"{l}. {text_map.get(l, '')}",
        key="choice",
    )

    cols = st.columns(3)
    submit_clicked = cols[0].button("Submit", use_container_width=True)
    restart_clicked = cols[1].button("Restart", use_container_width=True)
    next_clicked = cols[2].button("Next", use_container_width=True)

    # Handle restart
    if restart_clicked:
        st.session_state.state = {"index": 0, "score": 0, "answered": False}
        # reset selection
        if "choice" in st.session_state:
            del st.session_state["choice"]
        st.rerun()

    # Handle next question (sequential Part6 連続空所 or regenerate with current/randomized params)
    if next_clicked:
        _status2 = st.empty()
        _status2.info("Generating a question…")
        try:
                part_num = int(section_value) if section_value in (5, 6, 7) else 7
                genre_map = {
                    "Internal Notice": "notice",
                    "Advertisement": "advertisement",
                    "Review": "review",
                    "FAQ": "faq",
                    "Timetable/Schedule": "schedule",
                    "Press Release": "press_release",
                    "Policy": "policy",
                    "Invoice/Payment": "invoice",
                    "Menu": "menu",
                    "Event": "event",
                    "Weather Alert": "weather",
                    "Job Posting": "job_posting",
                    "Parking Rates": "parking",
                    "Social Post": "social_post",
                    "Interview Schedule": "interview",
                    "Newsletter": "newsletter",
                    "Manual/Instructions": "manual",
                    "Recall Notice": "recall_notice",
                    "Minutes": "minutes",
                    "Survey": "survey",
                }
                domain_map = {
                    "IT": "it",
                    "Manufacturing": "manufacturing",
                    "Logistics": "logistics",
                    "Medical": "medical",
                    "Finance": "finance",
                    "HR": "hr",
                    "Marketing": "marketing",
                    "Education": "education",
                    "Hospitality": "hospitality",
                    "Retail": "retail",
                    "Real Estate": "realestate",
                    "Energy": "energy",
                    "Legal": "legal",
                    "Public": "public",
                    "Aviation/Travel": "aviation",
                    "Food Service": "food",
                    "Construction": "construction",
                    "E-commerce": "ecommerce",
                    "Support": "support",
                }
                # 連続空所モードを撤去（常に新規生成）

                # ここから通常の再生成（ランダム化対応）
                effective_difficulty = difficulty
                effective_genre_label = genre_label
                effective_domain_label = domain_label
                effective_p7_length = p7_length
                if randomize_params:
                    part_num = random.choice([5, 6, 7])
                    effective_difficulty = random.choice(["easy", "medium", "hard"])
                    effective_genre_label = random.choice(list(genre_map.keys()))
                    effective_domain_label = random.choice(list(domain_map.keys()))
                    effective_p7_length = random.choice(["short", "medium", "long"])
                # Always use a fresh random seed per generation
                seed_opt = random.randint(1, 2**31 - 1)
                data = _do_generate(
                    engine, part_num, seed_opt, effective_p7_length, model_preset, openai_key,
                    difficulty=effective_difficulty,
                    genre=genre_map.get(effective_genre_label),
                    domain=domain_map.get(effective_domain_label),
                )
                data = filter_reading_only(data)
                questions = collect_questions(data)[:1]
                # 効果的パラメータをセッションに保存（連続空所の次の設問でも利用）
                st.session_state._effective_params = {
                    "p7_length": effective_p7_length,
                    "difficulty": effective_difficulty,
                    "genreLabel": effective_genre_label,
                    "genre": genre_map.get(effective_genre_label),
                    "domainLabel": effective_domain_label,
                    "domain": domain_map.get(effective_domain_label),
                    "part": part_num,
                }
                if not questions:
                    fb = _fallback_dataset(part_num)
                    fb_q = collect_questions(fb)
                    st.session_state.dataset = {"questions": fb_q}
                    q = fb_q[0]
                    letters: List[str] = []
                    text_map: Dict[str, str] = {}
                    for i, opt in enumerate(q.get("options", [])):
                        letter = option_to_letter(opt) or chr(ord("A") + i)
                        text = strip_option_label(opt)
                        letters.append(letter)
                        text_map[letter] = text
                    item = {
                        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                        "engine": engine,
                        "model": model_preset,
                        "p7_length": effective_p7_length,
                        "difficulty": effective_difficulty,
                        "genreLabel": effective_genre_label,
                        "genre": genre_map.get(effective_genre_label),
                        "domainLabel": effective_domain_label,
                        "domain": domain_map.get(effective_domain_label),
                        "part": q.get("_part"),
                        "partName": q.get("_part_name"),
                        "stem": derive_stem(q),
                        "options": [{"letter": l, "text": text_map.get(l, "")} for l in letters],
                        "answer": normalize_answer_letter(q.get("answer")),
                        "explanationJa": q.get("explanationJa", ""),
                        "context": q.get("context") or {},
                    }
                    st.session_state.history.append(item)
                    _autosave_history_item(item, autosave_enabled, autosave_dir)
                else:
                    st.session_state.dataset = {"questions": questions}
                    q = questions[0]
                    letters: List[str] = []
                    text_map: Dict[str, str] = {}
                    for i, opt in enumerate(q.get("options", [])):
                        letter = option_to_letter(opt) or chr(ord("A") + i)
                        text = strip_option_label(opt)
                        letters.append(letter)
                        text_map[letter] = text
                    item = {
                        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                        "engine": engine,
                        "model": model_preset,
                        "p7_length": effective_p7_length,
                        "difficulty": effective_difficulty,
                        "genreLabel": effective_genre_label,
                        "genre": genre_map.get(effective_genre_label),
                        "domainLabel": effective_domain_label,
                        "domain": domain_map.get(effective_domain_label),
                        "part": q.get("_part"),
                        "partName": q.get("_part_name"),
                        "stem": derive_stem(q),
                        "options": [{"letter": l, "text": text_map.get(l, "")} for l in letters],
                        "answer": normalize_answer_letter(q.get("answer")),
                        "explanationJa": q.get("explanationJa", ""),
                        "context": q.get("context") or {},
                    }
                    st.session_state.history.append(item)
                    _autosave_history_item(item, autosave_enabled, autosave_dir)
                st.session_state.state = {"index": 0, "score": 0, "answered": False}
                _status2.success("Generation completed.")
                time.sleep(0.3)
                _status2.empty()
        except Exception as e:
            part_num = 7
            try:
                part_num = int(section_value) if section_value in (5, 6, 7) else 7
            except Exception:
                pass
            fb = _fallback_dataset(part_num)
            fb_q = collect_questions(fb)
            st.session_state.dataset = {"questions": fb_q}
            st.session_state.state = {"index": 0, "score": 0, "answered": False}
            _status2.warning(f"Failed to generate. Showing fallback: {e}")

    # Handle submit
    if submit_clicked and not state.get("answered"):
        if choice:
            letter = choice  # radio returns the letter directly
            correct_letter = normalize_answer_letter(q.get("answer")) or ""
            is_correct = (letter == correct_letter)
            new_score = int(state.get("score", 0)) + (1 if is_correct else 0)
            st.session_state.state = {"index": idx, "score": new_score, "answered": True}
            # update last history entry with user answer and correctness
            if st.session_state.history:
                st.session_state.history[-1]["userAnswer"] = letter
                st.session_state.history[-1]["correct"] = bool(is_correct)
            st.rerun()

    # Feedback and Summary
    state = st.session_state.state
    if state.get("answered"):
        correct_letter = normalize_answer_letter(q.get("answer")) or "?"
        correct_text = text_map.get(correct_letter, "")
        if correct_text:
            st.success(f"Correct: {correct_letter}. {correct_text}")
        else:
            st.success(f"Correct: {correct_letter}")
        st.info(f"Explanation (JA): {q.get('explanationJa','')}")
    st.write(f"Score: {state.get('score',0)}/{len(questions)}")

    # Export buttons (JSON / CSV)
    export = {
        "part": q.get("_part"),
        "partName": q.get("_part_name"),
        "stem": stem,
        "options": [{"letter": l, "text": text_map.get(l, "")} for l in letters],
        "answer": normalize_answer_letter(q.get("answer")),
        "explanationJa": q.get("explanationJa", ""),
        "context": ctx_obj,
    }

    json_bytes = json.dumps(export, ensure_ascii=False, indent=2).encode("utf-8")
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    header = [
        "part", "partName", "stem", "optionA", "optionB", "optionC", "optionD", "answer", "explanationJa"
    ]
    writer.writerow(header)
    row = [
        export["part"],
        export["partName"],
        export["stem"],
        text_map.get("A", ""),
        text_map.get("B", ""),
        text_map.get("C", ""),
        text_map.get("D", ""),
        export["answer"],
        export["explanationJa"],
    ]
    writer.writerow(row)
    csv_bytes = csv_buf.getvalue().encode("utf-8-sig")

    # 全履歴のダウンロード用データを先に準備
    all_json = json.dumps(st.session_state.history, ensure_ascii=False, indent=2).encode("utf-8")
    all_csv_buf = io.StringIO()
    w = csv.writer(all_csv_buf)
    header2 = [
        "timestamp","engine","model","p7_length","difficulty","genre","genreLabel","domain","domainLabel",
        "part","partName","stem","optionA","optionB","optionC","optionD","answer","explanationJa",
        "groupId","blankIndex","blankCount"
    ]
    w.writerow(header2)
    for item in st.session_state.history:
        opts_map = {o["letter"]: o["text"] for o in item.get("options", [])}
        w.writerow([
            item.get("timestamp",""), item.get("engine",""), item.get("model",""), item.get("p7_length",""),
            item.get("difficulty",""), item.get("genre",""), item.get("genreLabel",""),
            item.get("domain",""), item.get("domainLabel",""),
            item.get("part",""), item.get("partName",""), item.get("stem",""),
            opts_map.get("A",""), opts_map.get("B",""), opts_map.get("C",""), opts_map.get("D",""),
            item.get("answer",""), item.get("explanationJa",""),
            item.get("groupId",""), item.get("blankIndex",""), item.get("blankCount",""),
        ])
    all_csv_bytes = all_csv_buf.getvalue().encode("utf-8-sig")

    # ボタン群を左詰めで横並びに（右側は大きな余白カラム）
    dcols = st.columns([1, 1, 1, 1, 8])
    with dcols[0]:
        st.download_button(
            label="Download JSON",
            data=json_bytes,
            file_name="toeic_question.json",
            mime="application/json",
        )
    with dcols[1]:
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name="toeic_question.csv",
            mime="text/csv",
        )
    with dcols[2]:
        st.download_button(
            label="Download ALL (JSON)",
            data=all_json,
            file_name="toeic_questions_all.json",
            mime="application/json",
        )
    with dcols[3]:
        st.download_button(
            label="Download ALL (CSV)",
            data=all_csv_bytes,
            file_name="toeic_questions_all.csv",
            mime="text/csv",
        )

    with st.expander("History (All)"):
        st.write(f"Total records: {len(st.session_state.history)}")
        if st.button("Clear History"):
            st.session_state.history = []
            st.success("History cleared.")
        # Review: pick an item and load to dataset
        if st.session_state.history:
            options = [
                f"{i+1}. {h.get('timestamp','')} | P{h.get('part','?')} | {h.get('genreLabel','')} | {h.get('stem','')[:40]}" for i, h in enumerate(st.session_state.history)
            ]
            sel = st.selectbox("Select to review", options)
            if st.button("Load selected into quiz"):
                idx_sel = options.index(sel)
                h = st.session_state.history[idx_sel]
                # reconstruct single-question dataset
                letters = [o.get("letter","?") for o in h.get("options", [])]
                ds_q = {
                    "_part": h.get("part"),
                    "_part_name": h.get("partName"),
                    "stem": h.get("stem"),
                    "options": [f"{l}. {o.get('text','')}" for l, o in zip(letters, h.get("options", []))],
                    "answer": h.get("answer"),
                    "explanationJa": h.get("explanationJa",""),
                    "context": h.get("context", {}),
                }
                st.session_state.dataset = {"questions": [ds_q]}
                st.session_state.state = {"index": 0, "score": 0, "answered": False}
                st.success("Loaded from history.")

    # Dashboard: simple stats
    with st.expander("Dashboard (Accuracy & Distribution)", expanded=False):
        hist = st.session_state.history
        total = len(hist)
        if total == 0:
            st.info("No data yet. Solve a few questions first.")
        else:
            answered = [h for h in hist if h.get("userAnswer")]
            correct = sum(1 for h in answered if h.get("correct") is True)
            st.write(f"Overall: {correct}/{len(answered)} correct ({(100*correct/len(answered)) if answered else 0:.1f}%)")

            # by part
            part_stats: Dict[str, Dict[str, int]] = {}
            for h in answered:
                p = str(h.get("part","?"))
                part_stats.setdefault(p, {"n":0, "c":0})
                part_stats[p]["n"] += 1
                if h.get("correct"):
                    part_stats[p]["c"] += 1
            if part_stats:
                st.write("By Part:")
                for p, s in sorted(part_stats.items()):
                    rate = (100*s["c"]/s["n"]) if s["n"] else 0
                    st.write(f"- Part {p}: {s['c']}/{s['n']} ({rate:.1f}%)")

            # by genreLabel
            genre_stats: Dict[str, Dict[str, int]] = {}
            for h in answered:
                g = str(h.get("genreLabel",""))
                genre_stats.setdefault(g, {"n":0, "c":0})
                genre_stats[g]["n"] += 1
                if h.get("correct"):
                    genre_stats[g]["c"] += 1
            if genre_stats:
                st.write("By Genre:")
                for g, s in sorted(genre_stats.items(), key=lambda kv: (-kv[1]['n'], kv[0])):
                    rate = (100*s["c"]/s["n"]) if s["n"] else 0
                    st.write(f"- {g}: {s['c']}/{s['n']} ({rate:.1f}%)")

            # Recent table (last 10)
            st.write("Recent 10:")
            recents = answered[-10:]
            rows = []
            for h in recents:
                rows.append({
                    "time": h.get("timestamp",""),
                    "part": h.get("part",""),
                    "genre": h.get("genreLabel",""),
                    "stem": (h.get("stem","")[:60] + ("…" if len(h.get("stem",""))>60 else "")),
                    "your": h.get("userAnswer",""),
                    "correct": h.get("answer",""),
                    "✓": "✔" if h.get("correct") else "✖",
                })
            try:
                import pandas as _pd  # type: ignore
                st.dataframe(_pd.DataFrame(rows))
            except Exception:
                # fallback plain table
                st.write(rows)
