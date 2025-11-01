from __future__ import annotations

from typing import Any, Dict, List

from dash import Dash, html, dcc, Input, Output, State, no_update

from toeic_generator import generate_dataset


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


def option_to_letter(opt_text: str):
    if len(opt_text) >= 2 and opt_text[1] == ".":
        c = opt_text[0].upper()
        if c in ("A", "B", "C", "D"):
            return c
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


app = Dash(__name__)

app.layout = html.Div([
    html.H2("TOEIC Mock (Reading) - Dash"),

    html.Div([
        html.Div([
            html.Label("Engine"),
            dcc.Dropdown(
                id="engine",
                options=[
                    {"label": "Local Generator", "value": "local"},
                    {"label": "OpenAI (ChatGPT)", "value": "openai"},
                ],
                value="local",
                clearable=False,
                style={"width": 200},
            ),
        ]),
        html.Div([
            html.Label("Section (Part)"),
            dcc.Dropdown(
                id="section-dd",
                options=[
                    {"label": "Part 5", "value": 5},
                    {"label": "Part 6", "value": 6},
                    {"label": "Part 7", "value": 7},
                ],
                value=7,
                clearable=False,
                style={"width": 180},
            ),
        ]),
        html.Div([
            html.Label("Seed"),
            dcc.Input(id="seed", type="number", value=42, step=1, style={"width": 160}),
        ]),
        html.Div([
            html.Label("Model (OpenAI)"),
            dcc.Input(id="model", type="text", value="gpt-5", style={"width": 200}),
        ]),
        html.Div([
            html.Label("P7 Passage Length"),
            dcc.Dropdown(
                id="p7-length",
                options=[
                    {"label": "Short", "value": "short"},
                    {"label": "Medium", "value": "medium"},
                    {"label": "Long", "value": "long"},
                ],
                value="long",
                clearable=False,
                style={"width": 160},
            ),
        ]),
        html.Button("Load One Question", id="load-btn"),
    ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "alignItems": "end"}),

    html.Hr(),

    dcc.Store(id="dataset-store"),  # 単一大問
    dcc.Store(id="state-store", data={"index": 0, "score": 0, "answered": False}),

    html.Div(id="status-area", style={"minHeight": "1.5rem", "marginBottom": "6px", "color": "#c00"}),

    dcc.Loading(id="loading", type="circle", children=html.Div(id="question-area")),

    html.Div(id="feedback"),

    html.Div([
        html.Button("Submit", id="submit-btn"),
        html.Button("Restart", id="restart-btn"),
    ], style={"display": "flex", "gap": "8px", "marginTop": "8px"}),

    html.Div(id="summary", style={"marginTop": "16px"}),
])


@app.callback(
    Output("dataset-store", "data"),
    Output("state-store", "data"),
    Input("load-btn", "n_clicks"),
    State("engine", "value"),
    State("section-dd", "value"),
    State("seed", "value"),
    State("p7-length", "value"),
    State("model", "value"),
    prevent_initial_call=True,
)
def on_load(n_clicks, engine, section_value, seed, p7_length, model):
    try:
        part_num = int(section_value) if section_value in (5, 6, 7) else 7
        seed_val = None if seed in (None, "") else int(seed)
        if engine == "openai":
            try:
                from llm_generator import generate_dataset_openai
                data = generate_dataset_openai(
                    title="TOEIC Mock - Single Question (LLM)",
                    part=part_num,
                    seed=seed_val,
                    p7_length=(p7_length or "long"),
                    model=(model or "gpt-5"),
                )
            except Exception as e:
                print("LLM error:", e)
                data = _fallback_dataset(part_num)
        else:
            data = generate_dataset(
                title="TOEIC Mock - Single Question",
                per_part=1,
                parts=[part_num],
                seed=seed_val,
                p7_length=(p7_length or "long"),
            )
        data = filter_reading_only(data)
        questions = collect_questions(data)[:1]
        if not questions:
            fb = _fallback_dataset(part_num)
            fb_q = collect_questions(fb)
            return {"questions": fb_q}, {"index": 0, "score": 0, "answered": False}
        return {"questions": questions}, {"index": 0, "score": 0, "answered": False}
    except Exception as e:
        print("Load error:", e)
        try:
            part_num = int(section_value) if section_value in (5, 6, 7) else 7
        except Exception:
            part_num = 7
        fb = _fallback_dataset(part_num)
        fb_q = collect_questions(fb)
        return {"questions": fb_q}, {"index": 0, "score": 0, "answered": False}


app.clientside_callback(
    """
    function(n_clicks, dataset) {
        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered || ctx.triggered.length === 0) {
            return ["", false, false, false, false, false, false];
        }
        const prop = ctx.triggered[0].prop_id;
        // When load button clicked -> set busy UI
        if (prop.startsWith("load-btn.n_clicks")) {
            if (!n_clicks) {
                return ["", false, false, false, false, false, false];
            }
            return ["問題を生成しています…", true, true, true, true, true, true];
        }
        // When dataset updated -> clear busy UI
        if (prop.startsWith("dataset-store.data")) {
            return ["", false, false, false, false, false, false];
        }
        return ["", false, false, false, false, false, false];
    }
    """,
    Output("status-area", "children"),
    Output("load-btn", "disabled"),
    Output("engine", "disabled"),
    Output("section-dd", "disabled"),
    Output("seed", "disabled"),
    Output("model", "disabled"),
    Output("p7-length", "disabled"),
    Input("load-btn", "n_clicks"),
    Input("dataset-store", "data"),
)


@app.callback(
    Output("question-area", "children"),
    Output("feedback", "children"),
    Output("summary", "children"),
    Input("dataset-store", "data"),
    Input("state-store", "data"),
)
def render_question(dataset, state):
    if not dataset or not dataset.get("questions"):
        return html.Div("データが未読み込みです。"), "", ""
    questions: List[Dict[str, Any]] = dataset["questions"]
    idx = max(0, min(int(state.get("index", 0)), len(questions) - 1)) if state else 0
    q = questions[idx]

    stem = derive_stem(q)
    ctx_obj = q.get("context") or {}

    extras: List[Any] = []
    if isinstance(ctx_obj.get("conversation"), list):
        for t in ctx_obj["conversation"]:
            extras.append(html.Div(f"{t.get('speaker', '?')}: {t.get('text', '')}"))
    if ctx_obj.get("text"):
        extras.append(html.Pre(
            ctx_obj.get("text"),
            style={"whiteSpace": "pre-wrap", "overflowY": "auto", "maxHeight": "24rem", "border": "1px solid #eee", "padding": "8px"}
        ))
    if ctx_obj.get("passage"):
        extras.append(html.Pre(
            ctx_obj.get("passage"),
            style={"whiteSpace": "pre-wrap", "overflowY": "auto", "maxHeight": "24rem", "border": "1px solid #eee", "padding": "8px"}
        ))

    opts = q.get("options", [])
    letters = []
    radio_options = []
    for opt in opts:
        letter = option_to_letter(opt) or chr(ord('A') + len(letters))
        letters.append(letter)
        radio_options.append({"label": opt, "value": letter})

    question_ui = html.Div([
        html.Div(f"[{idx+1}/{len(questions)}] Part {q.get('_part')}: {q.get('_part_name')}",
                 style={"fontWeight": "bold", "marginBottom": "4px"}),
        html.Div(stem, style={"marginBottom": "8px"}),
        html.Div(extras, style={"marginBottom": "8px"}),
        dcc.RadioItems(id="choice", options=radio_options, value=None),
    ])

    fb = html.Div("")
    summ = html.Div("")
    if state:
        answered = state.get("answered", False)
        score = state.get("score", 0)
        if answered:
            fb = html.Div([
                html.Div("採点済み", style={"fontWeight": "bold"}),
                html.Div(f"正解: {q.get('answer')}") ,
                html.Div(f"解説: {q.get('explanationJa', '')}"),
            ], style={"marginTop": "6px", "padding": "6px", "border": "1px solid #ccc"})
        summ = html.Div(f"Score: {score}/{len(questions)}")

    return question_ui, fb, summ


@app.callback(
    Output("state-store", "data", allow_duplicate=True),
    Input("submit-btn", "n_clicks"),
    State("dataset-store", "data"),
    State("state-store", "data"),
    State("choice", "value"),
    prevent_initial_call=True,
)
def on_submit(n_clicks, dataset, state, choice_value):
    if not dataset or not dataset.get("questions") or not state:
        return no_update
    if state.get("answered"):
        return no_update
    idx = int(state.get("index", 0))
    questions: List[Dict[str, Any]] = dataset["questions"]
    q = questions[idx]
    if not choice_value:
        return no_update
    is_correct = (choice_value == q.get("answer"))
    new_score = int(state.get("score", 0)) + (1 if is_correct else 0)
    return {"index": idx, "score": new_score, "answered": True}


    # シンプル版では待機/エラーの状態管理は表示しない


@app.callback(
    Output("state-store", "data", allow_duplicate=True),
    Input("restart-btn", "n_clicks"),
    State("dataset-store", "data"),
    prevent_initial_call=True,
)
def on_restart(n_clicks, dataset):
    if not dataset or not dataset.get("questions"):
        return no_update
    return {"index": 0, "score": 0, "answered": False}


    # シンプル版では初回オートロードも行わない


if __name__ == "__main__":
    app.run_server(host="127.0.0.1", port=8050, debug=True)
