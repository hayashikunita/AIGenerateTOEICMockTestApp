from __future__ import annotations

import random
import datetime as _dt
from typing import Any, Dict, List, Tuple


# 型エイリアス
Question = Dict[str, Any]
PartBlock = Dict[str, Any]
Dataset = Dict[str, Any]


# ---------------- Domain Lexicon Helper ----------------
def _domain_lex(domain: str | None) -> Dict[str, Any]:
    """Return domain-specific lexicon: nouns, departments, companies, ad_item.

    Known domain keys (examples):
    - it, manufacturing, logistics, medical
    - finance, hr, marketing, education, hospitality, retail, realestate,
      energy, legal, public, aviation, food, construction, ecommerce, support
    """
    d = (domain or "").lower()
    conf = {
        "nouns": ["report", "proposal", "contract", "shipment", "agenda", "policy"],
        "depts": ["finance", "HR", "marketing", "IT", "operations"],
        "companies": ["our company", "the vendor", "the client", "the committee", "the department"],
        "ad_item": "membership",
    }
    table = {
        "it": {
            "nouns": ["report", "ticket", "deployment", "release notes", "specification"],
            "depts": ["IT", "QA", "security", "platform", "infrastructure"],
            "companies": ["our team", "the vendor", "the client", "the committee", "the department"],
            "ad_item": "cloud backup plan",
        },
        "manufacturing": {
            "nouns": ["report", "proposal", "assembly plan", "maintenance log", "inspection record"],
            "depts": ["production", "quality", "engineering", "logistics", "procurement"],
            "companies": ["our factory", "the supplier", "the plant", "the committee", "the department"],
            "ad_item": "maintenance toolkit",
        },
        "logistics": {
            "nouns": ["shipment", "manifest", "waybill", "delivery schedule", "inventory report"],
            "depts": ["operations", "dispatch", "warehouse", "customs", "fleet"],
            "companies": ["our company", "the carrier", "the client", "the warehouse", "the department"],
            "ad_item": "express delivery option",
        },
        "medical": {
            "nouns": ["report", "consent form", "survey", "schedule", "policy"],
            "depts": ["administration", "nursing", "billing", "pharmacy", "radiology"],
            "companies": ["our clinic", "the hospital", "the lab", "the committee", "the department"],
            "ad_item": "health screening package",
        },
        "finance": {
            "nouns": ["invoice", "balance sheet", "statement", "budget", "ledger"],
            "depts": ["accounting", "audit", "treasury", "compliance", "finance"],
            "companies": ["our firm", "the client", "the bank", "the auditor", "the department"],
            "ad_item": "small-business loan consultation",
        },
        "hr": {
            "nouns": ["policy", "timesheet", "benefits form", "onboarding packet", "schedule"],
            "depts": ["HR", "recruiting", "training", "payroll", "compliance"],
            "companies": ["our HR team", "the recruiter", "the applicant", "the manager", "the department"],
            "ad_item": "employee wellness program",
        },
        "marketing": {
            "nouns": ["campaign brief", "press kit", "ad copy", "media plan", "newsletter"],
            "depts": ["marketing", "PR", "design", "sales", "digital"],
            "companies": ["our agency", "the client", "the sponsor", "the committee", "the department"],
            "ad_item": "social media analytics suite",
        },
        "education": {
            "nouns": ["syllabus", "schedule", "registration form", "survey", "policy"],
            "depts": ["admissions", "student affairs", "faculty", "library", "IT"],
            "companies": ["our school", "the university", "the department", "the committee", "the registrar"],
            "ad_item": "online course bundle",
        },
        "hospitality": {
            "nouns": ["reservation", "menu", "event order", "invoice", "policy"],
            "depts": ["front desk", "housekeeping", "banquet", "kitchen", "sales"],
            "companies": ["our hotel", "the restaurant", "the venue", "the concierge", "the department"],
            "ad_item": "seasonal dining plan",
        },
        "retail": {
            "nouns": ["inventory report", "price list", "return policy", "promotion", "invoice"],
            "depts": ["store operations", "merchandising", "customer service", "logistics", "marketing"],
            "companies": ["our store", "the supplier", "the warehouse", "the brand", "the department"],
            "ad_item": "loyalty membership",
        },
        "realestate": {
            "nouns": ["lease", "inspection report", "listing", "schedule", "policy"],
            "depts": ["property", "leasing", "sales", "maintenance", "compliance"],
            "companies": ["our agency", "the landlord", "the tenant", "the committee", "the department"],
            "ad_item": "open house tour",
        },
        "energy": {
            "nouns": ["maintenance log", "outage notice", "safety record", "inspection report", "proposal"],
            "depts": ["operations", "maintenance", "safety", "compliance", "engineering"],
            "companies": ["our utility", "the plant", "the contractor", "the committee", "the department"],
            "ad_item": "home energy audit",
        },
        "legal": {
            "nouns": ["contract", "brief", "case file", "policy", "notice"],
            "depts": ["legal", "compliance", "litigation", "IP", "risk"],
            "companies": ["our firm", "the client", "the court", "the committee", "the department"],
            "ad_item": "contract review service",
        },
        "public": {
            "nouns": ["notice", "agenda", "public comment", "policy", "survey"],
            "depts": ["city council", "planning", "public works", "transport", "parks"],
            "companies": ["the city", "the county", "the agency", "the board", "the department"],
            "ad_item": "community workshop",
        },
        "aviation": {
            "nouns": ["itinerary", "boarding pass", "notice", "schedule", "policy"],
            "depts": ["operations", "ground staff", "security", "maintenance", "customer service"],
            "companies": ["our airline", "the airport", "the carrier", "the authority", "the department"],
            "ad_item": "priority boarding option",
        },
        "food": {
            "nouns": ["menu", "invoice", "reservation", "order", "policy"],
            "depts": ["kitchen", "service", "banquet", "procurement", "marketing"],
            "companies": ["our cafe", "the restaurant", "the supplier", "the committee", "the department"],
            "ad_item": "meal subscription plan",
        },
        "construction": {
            "nouns": ["inspection report", "work order", "proposal", "schedule", "permit"],
            "depts": ["site", "engineering", "procurement", "safety", "logistics"],
            "companies": ["our contractor", "the client", "the vendor", "the council", "the department"],
            "ad_item": "equipment rental package",
        },
        "ecommerce": {
            "nouns": ["order", "return label", "invoice", "promotion", "inventory"],
            "depts": ["fulfillment", "customer support", "marketing", "IT", "analytics"],
            "companies": ["our shop", "the marketplace", "the seller", "the brand", "the department"],
            "ad_item": "free shipping upgrade",
        },
        "support": {
            "nouns": ["ticket", "knowledge base", "policy", "survey", "SLA"],
            "depts": ["support", "success", "training", "QA", "IT"],
            "companies": ["our support team", "the client", "the vendor", "the department", "the committee"],
            "ad_item": "premium support plan",
        },
    }
    conf.update(table.get(d, {}))
    return conf


def _label_options(options_plain: List[str], correct_index: int, rng: random.Random) -> Tuple[List[str], str]:
    """文字列の選択肢にA/B/C/Dのラベルを付けてシャッフルし、正解レターを返す。

    Args:
        options_plain: ラベル無しの選択肢テキスト配列
        correct_index: options_plain 内の正解インデックス
        rng: 乱数
    Returns:
        (ラベル付け＆シャッフル済みの配列, 正解レター)
    """
    idxs = list(range(len(options_plain)))
    rng.shuffle(idxs)
    labeled: List[str] = []
    answer_letter = "A"
    for i, idx in enumerate(idxs):
        letter = chr(ord('A') + i)
        text = options_plain[idx]
        labeled.append(f"{letter}. {text}")
        if idx == correct_index:
            answer_letter = letter
    return labeled, answer_letter


def _explain(prefix: str, jp: str) -> str:
    return f"{prefix}{jp}"


# ---------------- Part 1: Photographs ----------------

def gen_part1(count: int, rng: random.Random) -> PartBlock:
    subjects = [
        "A woman", "A man", "Two people", "Passengers", "Workers", "A chef", "A clerk",
    ]
    actions = [
        "arranging flowers", "typing on a laptop", "waiting at a counter", "standing on scaffolding",
        "riding bicycles", "loading boxes", "serving customers", "reading a document",
    ]
    places = [
        "in a cafe", "at an office desk", "at an airport check-in counter", "beside a building",
        "along a riverside path", "in a warehouse", "near a shop window",
    ]
    questions: List[Question] = []
    for i in range(count):
        s = rng.choice(subjects)
        a = rng.choice(actions)
        p = rng.choice(places)
        true_stmt = f"{s} is {a} {p}."
        distractors = [
            f"{s} is closing the window.",
            f"{s} is talking on the phone.",
            f"{s} is eating lunch.",
            f"{s} is waiting for a bus.",
        ]
        options_plain = [true_stmt] + rng.sample(distractors, k=3)
        correct_index = 0
        options, ans = _label_options(options_plain, correct_index, rng)
        q: Question = {
            "id": f"G-P1-Q{i+1}",
            "context": {
                "imageDescription": f"{s} is {a} {p}.",
            },
            "stem": "What is true about the picture?",
            "options": options,
            "answer": ans,
            "explanationJa": _explain("", "写真の描写に最も一致する文が正解です。"),
        }
        questions.append(q)
    return {
        "part": 1,
        "name": "Photographs",
        "instructions": "Choose the statement that best describes the picture.",
        "questions": questions,
    }


# ---------------- Part 2: Question-Response ----------------

def gen_part2(count: int, rng: random.Random) -> PartBlock:
    templates = [
        (
            "When is the budget meeting?",
            ["On Thursday afternoon.", "In the main conference room.", "I haven't met him."],
            0,
            "“いつ”に対して時刻/曜日で答えるのが自然。",
        ),
        (
            "Where is the training held?",
            ["In Room 402.", "At 3 p.m.", "About twenty people."],
            0,
            "“どこ”に対して場所で回答。",
        ),
        (
            "How much is the monthly fee?",
            ["It's $29 per month.", "By credit card.", "Yes, I already did."],
            0,
            "“いくら”に対して金額で回答。",
        ),
        (
            "Could you send me the invoice today?",
            ["Sure, I'll e-mail it by noon.", "It's on the second floor.", "Because we need it."],
            0,
            "依頼への肯定応答が自然。",
        ),
        (
            "Who will present the quarterly report?",
            ["Ms. Park from finance.", "In the auditorium.", "About 30 minutes."],
            0,
            "“誰が”に対して人物で回答。",
        ),
    ]
    questions: List[Question] = []
    for i in range(count):
        t = rng.choice(templates)
        prompt, opts, correct_idx, note = t
        options, ans = _label_options(opts, correct_idx, rng)
        q: Question = {
            "id": f"G-P2-Q{i+1}",
            "context": {"audioTranscript": prompt},
            "options": options,  # Part2は3択
            "answer": ans,
            "explanationJa": note,
        }
        questions.append(q)
    return {
        "part": 2,
        "name": "Question-Response",
        "instructions": "Listen to a question or statement and choose the best response.",
        "questions": questions,
    }


# ---------------- Part 3: Conversations ----------------

def gen_part3(count: int, rng: random.Random) -> PartBlock:
    bank = [
        (
            [
                {"speaker": "W", "text": "The printer on this floor is jammed again."},
                {"speaker": "M", "text": "I'll call IT right away."},
            ],
            "What will the man probably do?",
            ["Call the IT department.", "Buy more toner.", "Cancel the meeting.", "Go out for lunch."],
            0,
            "男性が “call IT” と発言。",
        ),
        (
            [
                {"speaker": "M", "text": "Did you receive the shipping confirmation?"},
                {"speaker": "W", "text": "Not yet, but they said it would be sent by 5 p.m."},
            ],
            "What is the status of the shipping confirmation?",
            ["It hasn't been received yet.", "It was delivered this morning.", "It was canceled.", "It needs to be printed."],
            0,
            "“Not yet” なので未受領。",
        ),
        (
            [
                {"speaker": "W", "text": "Let's move the presentation to Tuesday."},
                {"speaker": "M", "text": "Good idea. The clients will be back by then."},
            ],
            "When will the presentation likely be held?",
            ["Tuesday.", "Monday.", "Wednesday.", "Friday."],
            0,
            "“move ... to Tuesday” に対応。",
        ),
    ]
    questions: List[Question] = []
    for i in range(count):
        conv, qtext, opts, correct_idx, note = rng.choice(bank)
        options, ans = _label_options(opts, correct_idx, rng)
        q: Question = {
            "id": f"G-P3-Q{i+1}",
            "context": {"conversation": conv, "question": qtext},
            "options": options,
            "answer": ans,
            "explanationJa": note,
        }
        questions.append(q)
    return {
        "part": 3,
        "name": "Conversations",
        "instructions": "Listen to the conversation and choose the best answer.",
        "questions": questions,
    }


# ---------------- Part 4: Talks ----------------

def gen_part4(count: int, rng: random.Random) -> PartBlock:
    bank = [
        (
            "Welcome to the city museum. The gift shop is near the exit on the first floor.",
            "Where is the gift shop located?",
            ["Near the exit on the first floor.", "On the second floor.", "Next to the ticket counter.", "Across from the cafe."],
            0,
            "“first floor ... near the exit”。",
        ),
        (
            "This is a reminder: The maintenance crew will inspect the elevators tomorrow between 9 and 11 a.m.",
            "What will happen tomorrow morning?",
            ["Elevators will be inspected.", "A staff meeting will begin.", "A delivery will arrive.", "The office will be closed."],
            0,
            "“inspect the elevators”。",
        ),
        (
            "Due to severe weather, the 6 p.m. ferry has been canceled. We apologize for the inconvenience.",
            "What is the announcement about?",
            ["A schedule change.", "A price increase.", "A safety inspection.", "A new route."],
            0,
            "悪天候による運休＝スケジュール変更。",
        ),
    ]
    questions: List[Question] = []
    for i in range(count):
        talk, qtext, opts, correct_idx, note = rng.choice(bank)
        options, ans = _label_options(opts, correct_idx, rng)
        q: Question = {
            "id": f"G-P4-Q{i+1}",
            "context": {"talk": talk, "question": qtext},
            "options": options,
            "answer": ans,
            "explanationJa": note,
        }
        questions.append(q)
    return {
        "part": 4,
        "name": "Talks",
        "instructions": "Listen to the talk and choose the best answer.",
        "questions": questions,
    }


# ---------------- Part 5: Incomplete Sentences ----------------

def gen_part5(count: int, rng: random.Random, difficulty: str | None = None, genre: str | None = None, domain: str | None = None) -> PartBlock:
    """Part 5 の多様なパターンを生成。

    代表的な出題タイプ：
    - 前置詞 / 句動詞
    - 動詞の形（時制/ing/不定詞）
    - 接続詞 / 関係語
    - コロケーション（動詞+名詞 連語）
    - 比較 / 最上級
    """

    # domain によって語彙を切替（拡張版）
    _lex = _domain_lex(domain)
    nouns = _lex["nouns"]
    depts = _lex["depts"]
    companies = _lex["companies"]

    def p5_preposition() -> Tuple[str, List[str], int, str]:
        obj = rng.choice(["the online portal", "email", "the company website", "the shared drive"])
        stem = f"Employees are encouraged to submit feedback ______ {obj}."
        opts = ["through", "among", "across", "under"]
        note = (
            "空所には前置詞が入ります。『〜を通じて』は through を用います。among は『〜の間で（複数の中で）』、"
            "across は『〜の横断・一面に』、under は『〜の下に』で文脈に合いません。"
        )
        return stem, opts, 0, note

    def p5_verb_form() -> Tuple[str, List[str], int, str]:
        n = rng.choice(nouns)
        stem = f"The manager approved the {n} after carefully ______ the costs."
        opts = ["evaluating", "evaluated", "evaluation", "evaluates"]
        note = (
            "after は接続詞として用いると，後ろは動名詞（〜ing）を伴うのが自然です。carefully evaluating が適切。"
        )
        return stem, opts, 0, note

    def p5_conjunction() -> Tuple[str, List[str], int, str]:
        stem = "Our sales have increased steadily, ______ our market share remains small."
        opts = ["although", "because", "unless", "so"]
        note = "対立関係なので譲歩の although を用います。"
        return stem, opts, 0, note

    def p5_collocation() -> Tuple[str, List[str], int, str]:
        d = rng.choice(depts)
        stem = f"Please ______ the attached form to the {d} department by Friday."
        opts = ["submit", "repair", "cancel", "extend"]
        note = "書類は部署に『提出する』= submit がコロケーションとして自然です。"
        return stem, opts, 0, note

    def p5_comparative() -> Tuple[str, List[str], int, str]:
        stem = "This model is ______ than the previous version, making it ideal for travel."
        opts = ["lighter", "lightest", "more light", "light"]
        note = "比較級 than に合わせて lighter を選びます。"
        return stem, opts, 0, note

    def p5_quantifiers() -> Tuple[str, List[str], int, str]:
        stem = "There are ______ opportunities for advancement in this department."
        opts = ["a few", "few", "little", "a little"]
        note = "opportunities は可算名詞複数なので a few（少しはある）が最適。few は『ほとんどない』、little/a little は不可算向け。"
        return stem, opts, 0, note

    def p5_time_prep() -> Tuple[str, List[str], int, str]:
        stem = "The system will be down ______ two hours for maintenance."
        opts = ["for", "since", "during", "at"]
        note = "継続時間には for を用います。during は期間の中での出来事を述べる際に用いられます。"
        return stem, opts, 0, note

    def p5_phrasal_verb() -> Tuple[str, List[str], int, str]:
        stem = "Due to scheduling conflicts, we'll ______ the meeting to next week."
        opts = ["put off", "take off", "set off", "turn off"]
        note = "延期する＝ put off。take off は離陸/脱ぐ、set off は出発する、turn off は電源を切る。"
        return stem, opts, 0, note

    def p5_as_as() -> Tuple[str, List[str], int, str]:
        stem = "The new printer is as ______ as the old one."
        opts = ["fast", "fastly", "faster", "more fast"]
        note = "as + 形容詞 + as の比較。形容詞は fast。fastly は不可、faster/more fast は比較級で文に合わない。"
        return stem, opts, 0, note

    def p5_pronoun_agreement() -> Tuple[str, List[str], int, str]:
        stem = "Each of the employees ______ responsible for safety training."
        opts = ["is", "are", "be", "were"]
        note = "Each of + 複数名詞 でも動詞は単数 is をとる。"
        return stem, opts, 0, note

    def p5_subjunctive() -> Tuple[str, List[str], int, str]:
        stem = "It is essential that every member ______ the orientation on time."
        opts = ["complete", "completes", "completed", "will complete"]
        note = "that 節内で原形（仮定法現在）complete を用いる。"
        return stem, opts, 0, note

    def p5_passive() -> Tuple[str, List[str], int, str]:
        n = rng.choice(nouns)
        stem = f"The {n} ______ by the end of the day."
        opts = ["must be submitted", "must submit", "must be submitting", "must have submit"]
        note = "提出されなければならない＝受動 must be submitted。"
        return stem, opts, 0, note

    def p5_word_family() -> Tuple[str, List[str], int, str]:
        stem = "We need an ______ solution to reduce overall costs."
        opts = ["economical", "economic", "economics", "economically"]
        note = "形容詞『経済的な（節約的な）』は economical。economic は『経済の』、economics は学問名、economically は副詞。"
        return stem, opts, 0, note

    # 追加パターン
    def p5_relative_pronoun() -> Tuple[str, List[str], int, str]:
        stem = "The report, ______ was finalized yesterday, will be shared with all staff."
        opts = ["which", "that", "who", "whom"]
        note = "非制限用法（カンマあり）では which を用いる。that は不可。"
        return stem, opts, 0, note

    def p5_inversion() -> Tuple[str, List[str], int, str]:
        stem = "Only after the audit ______ the errors become apparent."
        opts = ["did", "do", "does", "had"]
        note = "Only + 副詞句 が文頭に来ると倒置（助動詞 do の過去 did）。"
        return stem, opts, 0, note

    def p5_parallelism() -> Tuple[str, List[str], int, str]:
        stem = "The position requires managing budgets, coordinating schedules, and ______."
        opts = ["communicating with stakeholders", "to communicate with stakeholders", "communication with stakeholders", "communicate with stakeholders"]
        note = "並列構造は -ing で統一：communicating が自然。"
        return stem, opts, 0, note

    def p5_articles() -> Tuple[str, List[str], int, str]:
        stem = "He is ______ experienced engineer."
        opts = ["an", "a", "the", "(no article)"]
        note = "母音音で始まる experienced の前は an。"
        return stem, opts, 0, note

    def p5_count_uncount() -> Tuple[str, List[str], int, str]:
        stem = "We need more ______ to complete the project."
        opts = ["equipment", "equipments", "equipmentes", "equipments are"]
        note = "equipment は不可算名詞で複数形にしない。"
        return stem, opts, 0, note

    def p5_fewer_less() -> Tuple[str, List[str], int, str]:
        stem = "We have ______ resources than last quarter."
        opts = ["fewer", "less", "little", "few"]
        note = "resources は可算複数 → fewer を用いる。"
        return stem, opts, 0, note

    def p5_conditional_third() -> Tuple[str, List[str], int, str]:
        stem = "If he ______ the report earlier, we could have fixed the issue."
        opts = ["had sent", "sent", "has sent", "would send"]
        note = "仮定法過去完了（過去の事実に反する仮定）→ had + p.p."
        return stem, opts, 0, note

    def p5_reported_speech() -> Tuple[str, List[str], int, str]:
        stem = "She said she ______ the files by noon."
        opts = ["would send", "will send", "sends", "is sending"]
        note = "時制の一致で would + 動詞の原形。"
        return stem, opts, 0, note

    def p5_adj_order() -> Tuple[str, List[str], int, str]:
        stem = "She bought a ______ laptop for travel."
        opts = ["lightweight new", "new lightweight", "new and lightweight", "lightweight of new"]
        note = "形容詞の語順：意見（new）→ 性質（lightweight）→ 名詞。『new lightweight』が自然。"
        return stem, opts, 1, note

    def p5_infinitive_after_adj() -> Tuple[str, List[str], int, str]:
        stem = "The task is easy ______."
        opts = ["to complete", "completing", "to completing", "completed"]
        note = "形容詞 + to 不定詞。easy to complete。"
        return stem, opts, 0, note

    def p5_collocation_take_note() -> Tuple[str, List[str], int, str]:
        stem = "Please take ______ of the new safety guidelines."
        opts = ["note", "notes", "a note", "noting"]
        note = "慣用表現：take note of（〜に留意する）。"
        return stem, opts, 0, note

    pattern_funcs = [
        p5_preposition,
        p5_verb_form,
        p5_conjunction,
        p5_collocation,
        p5_comparative,
        p5_quantifiers,
        p5_time_prep,
        p5_phrasal_verb,
        p5_as_as,
        p5_pronoun_agreement,
        p5_subjunctive,
        p5_passive,
        p5_word_family,
        # 追加
        p5_relative_pronoun,
        p5_inversion,
        p5_parallelism,
        p5_articles,
        p5_count_uncount,
        p5_fewer_less,
        p5_conditional_third,
        p5_reported_speech,
        p5_adj_order,
        p5_infinitive_after_adj,
        p5_collocation_take_note,
    ]
    # 難易度で軽く分岐（hard なら文法系を選びやすく）
    if difficulty == "hard":
        pattern_funcs = [
            p5_verb_form, p5_conjunction, p5_subjunctive, p5_passive,
            p5_word_family, p5_pronoun_agreement, p5_comparative, p5_preposition
        ]

    questions: List[Question] = []
    for i in range(count):
        stem, opts, correct_idx, note = rng.choice(pattern_funcs)()
        options, ans = _label_options([f"{x}" for x in opts], correct_idx, rng)
        q: Question = {
            "id": f"G-P5-Q{i+1}",
            "stem": stem,
            "options": options,
            "answer": ans,
            "explanationJa": note,
        }
        questions.append(q)
    return {
        "part": 5,
        "name": "Incomplete Sentences",
        "instructions": "Choose the word or phrase that best completes the sentence.",
        "questions": questions,
    }


# ---------------- Part 6: Text Completion ----------------

def gen_part6(count: int, rng: random.Random, difficulty: str | None = None, genre: str | None = None, domain: str | None = None) -> PartBlock:
    """Part 6: さまざまな文書種別の1文テキストに空欄を設定。"""

    def memo_type() -> Tuple[str, List[str], int, str]:
        return (
            "To all staff: Please 【_____】 your timesheets by Friday so payroll can be processed on time. Thank you.",
            ["submit", "repair", "cancel", "extend"],
            0,
            "timesheet は『提出する』= submit が自然。",
        )

    def notice_type() -> Tuple[str, List[str], int, str]:
        return (
            "Reminder: The parking lot will be closed for cleaning this weekend. Please 【_____】 alternative arrangements.",
            ["make", "made", "making", "to make"],
            0,
            "collocation として make arrangements（手配をする）。",
        )

    def email_type() -> Tuple[str, List[str], int, str]:
        return (
            "Dear Customer, Your order has been shipped and should arrive 【_____】 three business days.",
            ["within", "at", "on", "since"],
            0,
            "『〜以内に』は within。",
        )

    def apology_type() -> Tuple[str, List[str], int, str]:
        return (
            "We apologize for the delay in responding to your inquiry and appreciate your 【_____】.",
            ["patience", "patient", "patients", "patiently"],
            0,
            "appreciate の目的語に名詞 patience。",
        )

    def plan_type() -> Tuple[str, List[str], int, str]:
        return (
            "Our company is 【_____】 a new line of eco-friendly packaging next quarter.",
            ["launching", "launched", "to launch", "launch"],
            0,
            "be + V-ing で近い未来の確定予定を表現。",
        )

    def newsletter_type() -> Tuple[str, List[str], int, str]:
        return (
            "Newsletter: The team will host a workshop next month. Please 【_____】 if you plan to attend.",
            ["register", "registered", "registration", "to register"],
            0,
            "命令/依頼文では動詞の原形 register が自然。",
        )

    def ad_type() -> Tuple[str, List[str], int, str]:
        item = _domain_lex(domain)["ad_item"]
        text = f"Advertisement: Sign up now and get 20% off {item}. Offer 【_____】 March 31."
        opts = ["until", "since", "at", "on"]
        note = "期限は until が自然です。"
        return (text, opts, 0, note)

    def faq_type() -> Tuple[str, List[str], int, str]:
        text = "FAQ: Q) How can I reset my password? A) Please 【_____】 the instructions on the settings page."
        opts = ["follow", "follows", "to follow", "following"]
        note = "動詞の原形 follow を用いるのが自然です。"
        return (text, opts, 0, note)

    def paragraph_multi() -> Tuple[str, List[str], int, str]:
        # 段落に 2〜3 個の空欄（連続空所対応：本文中の空欄を番号付きで生成し、各空欄の選択肢を同時に用意）
        blanks = rng.choice([2, 3])
        base = "To all staff, \nWe are updating procedures this month to improve efficiency. "
        nouns = _domain_lex(domain)["nouns"]
        n1 = nouns[0] if nouns else "forms"
        n2 = nouns[1] if len(nouns) > 1 else "reports"
        # 空欄を番号付きで出力（例：【_____1】）
        base += f"Please 【_____1】 the {n1} and 【_____2】 the {n2} by Friday. "
        if blanks == 3:
            base += "We also ask you to 【_____3】 with your team to avoid delays."

        # 各空欄の選択肢セット（素の文字列）と正解インデックス
        blank_opts_plain: List[List[str]] = []
        blank_correct_idx: List[int] = []
        blank_notes: List[str] = []

        # 空欄1：提出（submit）
        blank_opts_plain.append(["submit", "repair", "cancel", "extend"])
        blank_correct_idx.append(0)
        blank_notes.append("提出は submit が自然です（空欄1）。")
        # 空欄2：もう一つの提出（ドメイン語彙に合わせても可だが簡易化して submit を正解に）
        blank_opts_plain.append(["submit", "review", "cancel", "extend"])
        blank_correct_idx.append(0)
        blank_notes.append("ここも『提出する』= submit が自然（空欄2）。")
        # 空欄3（ある場合）：チームでの調整
        if blanks == 3:
            blank_opts_plain.append(["coordinate", "communicate", "collaborate", "cooperate"])
            blank_correct_idx.append(0)
            blank_notes.append("遅延回避のために『調整する』= coordinate が最適（空欄3）。")

        # 各空欄についてラベル付けと正解レターを作成
        labeled_sets: List[List[str]] = []
        answer_letters: List[str] = []
        for i in range(blanks):
            opts_labeled, ans_letter = _label_options(blank_opts_plain[i], blank_correct_idx[i], rng)
            labeled_sets.append(opts_labeled)
            answer_letters.append(ans_letter)

        # 返却は『空欄1』に対する設問だが、context に全空欄の情報を格納（UI で連続空所を実現）
        # 最初の設問としては、空欄1の選択肢・答え・解説を返す
        note = "段落型の空欄（空欄1）。連続空所モードでは本文中の番号つき空欄を順に解答します。"
        # context に multi-blank 情報を格納
        group_id = f"P6-{rng.randrange(1_000_000, 9_999_999)}"
        context_text = base
        # context 情報は gen_part6 の呼び出し元で利用
        # 注意：戻り値の options/answer は空欄1のもの
        # multi-blank 情報は context 内に含める
        # Calling site will insert into question
        # → この関数の戻り値は後段で q にまとめられる
        opts_for_first = labeled_sets[0]
        correct_letter_first = answer_letters[0]
        # context の拡張は gen_part6 の q 生成部分で行う
        return (  # type: ignore[return-value]
            # text は gen_part6 の下で context に入れるため、ここは text を返しつつ、呼び出し側で差し替える
            # options/answer/note は空欄1用
            # text を返すのは既存の構造との整合のため
            context_text,
            opts_for_first,
            ord(correct_letter_first) - ord('A'),
            note,
        )

    patterns = [memo_type, notice_type, email_type, apology_type, plan_type, newsletter_type, ad_type, faq_type, paragraph_multi]
    
    # 追加パターン（さらに多様化）
    def outage_notice() -> Tuple[str, List[str], int, str]:
        text = "Notice: The service will be unavailable from 2 a.m. to 4 a.m. Please 【_____】 accordingly."
        opts = ["plan", "plans", "planning", "to plan"]
        note = "依頼/指示文では原形 plan。"
        return (text, opts, 0, note)

    def invitation_type() -> Tuple[str, List[str], int, str]:
        text = "Invitation: You are invited to our product launch event. Please 【_____】 by May 5."
        opts = ["RSVP", "RSVPs", "to RSVP", "RSVPed"]
        note = "ここでは動詞としての RSVP（原形）を用いる。"
        return (text, opts, 0, note)

    def confirmation_email() -> Tuple[str, List[str], int, str]:
        text = "Email: Thank you for your request. We have 【_____】 your form and will contact you soon."
        opts = ["received", "receive", "receiving", "to receive"]
        note = "受け取った＝過去分詞 received。"
        return (text, opts, 0, note)

    patterns += [outage_notice, invitation_type, confirmation_email]

    # 追加の文書タイプ（多様化）
    def press_release() -> Tuple[str, List[str], int, str]:
        text = "Press Release: Trendmore Inc. will launch a regional pilot next month. Please 【_____】 our website for details."
        opts = ["see", "seeing", "to see", "saw"]
        note = "指示文の原形 see（『参照してください』）。"
        return (text, opts, 0, note)

    def survey_announce() -> Tuple[str, List[str], int, str]:
        text = "Survey: All employees are invited to 【_____】 the questionnaire by Friday."
        opts = ["complete", "completed", "completing", "to complete"]
        note = "不定詞や分詞ではなく、命令・依頼的な原形 complete。"
        return (text, opts, 0, note)

    def shipping_delay() -> Tuple[str, List[str], int, str]:
        text = "Shipping Update: Your order is 【_____】 due to customs inspection."
        opts = ["delayed", "delay", "delaying", "to delay"]
        note = "受動の状態を表す delayed が自然。"
        return (text, opts, 0, note)

    def followup_email() -> Tuple[str, List[str], int, str]:
        text = "Email: Following up on our meeting, please 【_____】 the attached proposal."
        opts = ["review", "reviews", "reviewing", "to review"]
        note = "依頼文の原形 review。"
        return (text, opts, 0, note)

    def minutes_excerpt() -> Tuple[str, List[str], int, str]:
        text = "Minutes: Mr. Cho 【_____】 the budget revisions; the team agreed to submit feedback by Tuesday."
        opts = ["presented", "presents", "presenting", "to present"]
        note = "過去の出来事の記録 → 過去形 presented。"
        return (text, opts, 0, note)

    def policy_update2() -> Tuple[str, List[str], int, str]:
        text = "Policy Update: All visitors must 【_____】 at the front desk upon arrival."
        opts = ["sign in", "sign on", "sign at", "sign up"]
        note = "受付での手続きは sign in。sign up は登録。"
        return (text, opts, 0, note)

    def product_recall() -> Tuple[str, List[str], int, str]:
        text = "Recall Notice: If your unit shows signs of overheating, 【_____】 using it immediately."
        opts = ["stop", "stops", "to stop", "stopped"]
        note = "命令文の原形 stop。"
        return (text, opts, 0, note)

    def itinerary_snippet() -> Tuple[str, List[str], int, str]:
        text = "Itinerary: Flight JK210 departs at 09:15 and 【_____】 at 12:45."
        opts = ["arrives", "arrive", "arrived", "is arriving"]
        note = "三単現の arrives。"
        return (text, opts, 0, note)

    def manual_step() -> Tuple[str, List[str], int, str]:
        text = "Manual: To reset the device, 【_____】 the power button for ten seconds."
        opts = ["hold", "holds", "to hold", "holding"]
        note = "手順書の命令形：hold。"
        return (text, opts, 0, note)

    patterns += [
        press_release, survey_announce, shipping_delay, followup_email,
        minutes_excerpt, policy_update2, product_recall, itinerary_snippet, manual_step
    ]

    questions: List[Question] = []
    for i in range(count):
        picked = rng.choice(patterns)
        text, opts, correct_idx, note = picked()
        options, ans = _label_options([f"{x}" for x in opts], correct_idx, rng)
        # 連続空所（paragraph_multi）かどうかで context を拡張
        context: Dict[str, Any] = {"text": text}
        if picked.__name__ == "paragraph_multi":
            # paragraph_multi は text に番号付き空欄が含まれている
            # ここで multi-blank 情報を構築し、空欄1の設問として返す
            # 再実行して詳細を得る必要があるため、ローカル再構成
            blanks = 3 if "【_____3】" in text else 2
            # 再度同ロジックでオプションを作成（順序はすでに options/ans が空欄1に対して作成済み）
            # 空欄2/3 のセットを生成
            # 空欄2
            opts2_labeled, ans2 = _label_options(["submit", "review", "cancel", "extend"], 0, rng)
            # 空欄3（あれば）
            opts3_labeled, ans3 = _label_options(["coordinate", "communicate", "collaborate", "cooperate"], 0, rng) if blanks == 3 else ([], "A")
            context.update({
                "multiBlanks": True,
                "blankCount": blanks,
                "blankIndex": 0,  # この設問は空欄1
                "blankOptionsLabeled": [options, opts2_labeled] + ([opts3_labeled] if blanks == 3 else []),
                "blankAnswerLetters": [ans, ans2] + ([ans3] if blanks == 3 else []),
                "blankNotes": [note, "ここも『提出する』= submit が自然（空欄2）。"] + (["遅延回避のために『調整する』= coordinate が最適（空欄3）。"] if blanks == 3 else []),
                "groupId": f"P6-{rng.randrange(1_000_000, 9_999_999)}",
            })
        q: Question = {
            "id": f"G-P6-Q{i+1}",
            "context": context,
            "options": options,
            "answer": ans,
            "explanationJa": note,
        }
        questions.append(q)
    return {
        "part": 6,
        "name": "Text Completion",
        "instructions": "Read the text and choose the best option to complete the blank.",
        "questions": questions,
    }


# ---------------- Part 7: Reading ----------------

def _build_paragraph(rng: random.Random, target_sentences: int) -> str:
    subjects = [
        "Our company", "The community center", "A local nonprofit", "The city council",
        "The marketing team", "A travel agency", "This year’s organizing committee",
    ]
    actions = [
        "is planning", "has announced", "will introduce", "is preparing",
        "decided to launch", "started coordinating", "will expand",
    ]
    objects = [
        "a new outreach program", "an annual charity event", "a series of workshops",
        "an employee wellness initiative", "a weekend festival", "a pilot project",
    ]
    details = [
        "to support local businesses", "to improve public awareness",
        "to gather feedback from residents", "to foster collaboration across departments",
        "to help first-time participants", "to share practical skills",
    ]
    sentences: List[str] = []
    for _ in range(target_sentences):
        s = f"{rng.choice(subjects)} {rng.choice(actions)} {rng.choice(objects)} {rng.choice(details)}."
        sentences.append(s)
    return " ".join(sentences)


def _make_passage(rng: random.Random, length: str) -> str:
    if length == "long":
        p1 = _build_paragraph(rng, 5)
        p2 = _build_paragraph(rng, 5)
        p3 = _build_paragraph(rng, 4)
        return f"{p1}\n\n{p2}\n\n{p3}"
    if length == "medium":
        p1 = _build_paragraph(rng, 4)
        p2 = _build_paragraph(rng, 3)
        return f"{p1}\n\n{p2}"
    # short
    return _build_paragraph(rng, 3)


def gen_part7(count: int, rng: random.Random, length: str = "short", difficulty: str | None = None, genre: str | None = None, domain: str | None = None) -> PartBlock:
    def _p7_short_bank() -> List[tuple[str, str, List[str], int, str]]:
        bank: List[tuple[str, str, List[str], int, str]] = []
        # 基本の告知
        bank.append((
            "Notice: The downtown library will close at 5 p.m. on Friday for a private event. Regular hours resume Saturday.",
            "What will happen on Friday evening?",
            ["The library will host a private event.", "The library will extend its hours.", "The library will open a new branch.", "The library will be under renovation."],
            0,
            "private event のために閉館。",
        ))
        # FAQ 形式（IT 寄り）
        bank.append((
            "FAQ: How do I change my account e-mail? Go to Settings > Profile and select 'Update E-mail'.",
            "What should users do to change their e-mail?",
            ["Open the Settings page and update it.", "Contact customer support by phone.", "Fill out a paper form.", "Send a fax to the office."],
            0,
            "Settings > Profile の手順に従う。",
        ))
        # 時刻表/スケジュール
        bank.append((
            "Schedule: Airport Shuttle — Departures: 08:00, 09:30, 11:00. Returns: 14:00, 16:30, 19:00.",
            "When is the next shuttle after 9 a.m.?",
            ["09:30", "08:00", "11:00", "14:00"],
            0,
            "9時以降の最初は 09:30。",
        ))
        # 広告風（ドメインで語彙差し）
        prod = _domain_lex(domain)["ad_item"]
        bank.append((
            f"Ad: Sign up this week and get 30% off our {prod}.",
            "What is the main offer in the ad?",
            ["A 30% discount for sign-ups this week.", "A free trial for one month.", "A buy-one-get-one deal.", "A free upgrade for all users."],
            0,
            "this week の 30% 割引を告知。",
        ))
        # レビュー
        bank.append((
            "Review: The new model is lightweight and easy to carry, but the screen brightness could be higher.",
            "What is one criticism mentioned in the review?",
            ["The screen is not bright enough.", "It is too heavy.", "It is complicated to use.", "The battery drains too fast."],
            0,
            "brightness に不満。",
        ))
        # 追加: 告知文（施設メンテ）
        bank.append((
            "Notice: The cafeteria will be closed on Tuesday afternoon for equipment maintenance.",
            "What will happen on Tuesday afternoon?",
            ["The cafeteria will be closed.", "The cafeteria will extend hours.", "A new cafeteria will open.", "Free meals will be offered."],
            0,
            "メンテナンスのため閉鎖。",
        ))
        # 追加: 求人情報
        bank.append((
            "Job Posting: We are seeking a part-time receptionist with weekend availability.",
            "What is one requirement for the position?",
            ["Availability on weekends.", "A full-time schedule.", "Experience in construction.", "International travel."],
            0,
            "週末の勤務可能が条件。",
        ))
        # 追加: 請求書スニペット
        bank.append((
            "Invoice: Balance due by June 30. Please include the invoice number with your payment.",
            "When is the balance due?",
            ["By June 30.", "By June 15.", "On July 1.", "Within seven days."],
            0,
            "due by = 期限。",
        ))
        # 追加: ポリシー抜粋
        bank.append((
            "Policy: Personal devices must be kept in silent mode during meetings.",
            "What must employees do during meetings?",
            ["Keep personal devices in silent mode.", "Turn off all lights.", "Report to security.", "Wear ID badges at home."],
            0,
            "silent mode が要件。",
        ))
        # 追加: 返品FAQ
        bank.append((
            "FAQ: Can I return items without a receipt? Returns without a receipt are accepted for store credit only.",
            "What happens if you return an item without a receipt?",
            ["You receive store credit.", "You receive a full refund.", "The return is not accepted.", "You must pay a fee."],
            0,
            "store credit のみ。",
        ))
        # 追加: 列車時刻
        bank.append((
            "Schedule: Trains to Central — 08:10, 08:40, 09:05, 09:50.",
            "Which train departs after 9 a.m.?",
            ["09:05", "08:40", "08:10", "09:50"],
            0,
            "9時以降最初は 09:05。",
        ))
        # 追加: プレスリリース抜粋
        bank.append((
            "Press Release: Norvia Labs will open a new research center in August to expand its testing capacity.",
            "What is Norvia Labs planning to do?",
            ["Open a new research center.", "Close its main office.", "Discontinue testing services.", "Relocate overseas immediately."],
            0,
            "open a new research center と明記。",
        ))
        # 追加: メニュー抜粋
        bank.append((
            "Menu: Lunch Set includes soup, a main dish, and coffee or tea.",
            "What is included in the lunch set?",
            ["Soup and a main dish with a drink.", "Only a main dish.", "Dessert and coffee only.", "Two main dishes."],
            0,
            "includes の列挙に soup, main dish, and coffee or tea。",
        ))
        # 追加: 駐車料金
        bank.append((
            "Parking Rates: $3 per hour; maximum daily rate $12.",
            "How much is the maximum daily parking rate?",
            ["$12", "$3", "$6", "$9"],
            0,
            "maximum daily rate $12 と記載。",
        ))
        # 追加: イベントフライヤー
        bank.append((
            "Event: Community Cleanup — Saturday 9 a.m. Registration closes Thursday at 5 p.m.",
            "When does registration close?",
            ["Thursday at 5 p.m.", "Friday at noon.", "Saturday at 9 a.m.", "Sunday morning."],
            0,
            "Registration closes の時刻は Thursday 5 p.m.。",
        ))
        # 追加: 天気注意報
        bank.append((
            "Weather Alert: High winds expected overnight. Secure outdoor items.",
            "What does the alert advise people to do?",
            ["Secure outdoor items.", "Open all windows.", "Drive at high speed.", "Cancel indoor events."],
            0,
            "Secure outdoor items と明記。",
        ))
        # 追加: SNS投稿
        bank.append((
            "Post: Our pop-up store opens at 11 a.m. today — first 50 visitors get a free tote bag!",
            "What is offered to early visitors?",
            ["A free tote bag.", "A free lunch.", "A 70% discount.", "A free umbrella."],
            0,
            "first 50 visitors get a free tote bag。",
        ))
        # 追加: 面接スケジュール
        bank.append((
            "Interview Schedule: Candidates should arrive 15 minutes early and bring photo ID.",
            "What must candidates bring?",
            ["A photo ID.", "A recommendation letter.", "A passport-sized photo.", "A laptop."],
            0,
            "bring photo ID とある。",
        ))
        return bank

    questions: List[Question] = []
    for i in range(count):
        if length in ("medium", "long"):
            passage = _make_passage(rng, length)
            # 質問タイプを複数から選択
            if rng.random() < 0.5:
                stem = "What is the main purpose of the passage?"
                opts = [
                    "To announce or describe an upcoming initiative.",
                    "To provide technical instructions for repairs.",
                    "To advertise discounted products.",
                    "To issue a safety recall notice.",
                ]
                correct_idx = 0
                note = (
                    "段落全体が『新たな取り組みや計画の告知・説明』に一貫して言及しています。"
                )
            else:
                # 本文に典型的に含まれる『新規プログラム/ワークショップ/パイロット』などの言及を問う
                objects = [
                    "a new outreach program",
                    "a series of workshops",
                    "a pilot project",
                    "an employee wellness initiative",
                ]
                correct_obj = rng.choice(objects)
                stem = "Which of the following is mentioned in the passage?"
                opts = [
                    f"Plans to introduce {correct_obj}.",
                    "A recall of defective devices.",
                    "A storewide 50% discount.",
                    "Instructions to repair machinery.",
                ]
                correct_idx = 0
                note = "本文は新たな取り組みの導入を述べており、値引きや製品回収、修理手順は含まれていません。"
        else:
            short_bank = _p7_short_bank()
            # ジャンル指定がある場合は近いものを優先
            if genre == "faq":
                candidates = [b for b in short_bank if b[0].startswith("FAQ:")]
                if candidates:
                    passage, stem, opts, correct_idx, _ = rng.choice(candidates)
                else:
                    passage, stem, opts, correct_idx, _ = rng.choice(short_bank)
            elif genre == "schedule":
                candidates = [b for b in short_bank if b[0].startswith("Schedule:")]
                if candidates:
                    passage, stem, opts, correct_idx, _ = rng.choice(candidates)
                else:
                    passage, stem, opts, correct_idx, _ = rng.choice(short_bank)
            elif genre == "advertisement":
                candidates = [b for b in short_bank if b[0].startswith("Ad:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "review":
                candidates = [b for b in short_bank if b[0].startswith("Review:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            # 追加のジャンルフィルタ
            elif genre in ("notice", "internal_notice"):
                candidates = [b for b in short_bank if b[0].startswith("Notice:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "policy":
                candidates = [b for b in short_bank if b[0].startswith("Policy:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "press_release":
                candidates = [b for b in short_bank if b[0].startswith("Press Release:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "invoice":
                candidates = [b for b in short_bank if b[0].startswith("Invoice:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "menu":
                candidates = [b for b in short_bank if b[0].startswith("Menu:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "event":
                candidates = [b for b in short_bank if b[0].startswith("Event:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "weather":
                candidates = [b for b in short_bank if b[0].startswith("Weather Alert:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "job_posting":
                candidates = [b for b in short_bank if b[0].startswith("Job Posting:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "parking":
                candidates = [b for b in short_bank if b[0].startswith("Parking Rates:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "social_post":
                candidates = [b for b in short_bank if b[0].startswith("Post:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "interview":
                candidates = [b for b in short_bank if b[0].startswith("Interview Schedule:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            elif genre == "newsletter":
                candidates = [b for b in short_bank if b[0].startswith("Newsletter:")]
                passage, stem, opts, correct_idx, _ = rng.choice(candidates or short_bank)
            else:
                passage, stem, opts, correct_idx, _ = rng.choice(short_bank)
            # 短文は根拠フレーズを日本語で明示
            key_hint = ""
            if "private event" in passage:
                key_hint = "本文には『private event（貸切）』とあり、そのため金曜は閉館すると示されています。"
            elif "attached the draft agenda" in passage:
                key_hint = "『draft agenda を添付』し、火曜までに修正（edits）を送るよう依頼している旨が書かれています。"
            elif "Registration includes" in passage:
                key_hint = "『Registration includes ...』に T-shirt と refreshment が明示されています。"
            elif "The elevator is out of service" in passage:
                key_hint = "『エレベーターは使用不可』のため、『階段や貨物用エレベーターを使用』と代替手段が提示されています。"
            elif "battery life" in passage:
                key_hint = "レビューでは『battery life could be better』とあり、電池持ちへの不満が述べられています。"
            note = f"本文の記述から直接答えを特定できます。{key_hint}根拠となる語句に線を引いて確認すると正答の再現性が高まります。"
        options, ans = _label_options(opts, correct_idx, rng)
        q: Question = {
            "id": f"G-P7-Q{i+1}",
            "context": {"passage": passage},
            "stem": stem,
            "options": options,
            "answer": ans,
            "explanationJa": note,
        }
        questions.append(q)
    return {
        "part": 7,
        "name": "Reading Comprehension",
        "instructions": "Read the passage and choose the best answer.",
        "questions": questions,
    }


# ---------------- Dataset generator ----------------

def generate_dataset(title: str = "TOEIC Mock Test - Generated",
                      per_part: int = 3,
                      parts: List[int] | None = None,
                      seed: int | None = None,
                      p7_length: str | None = None,
                      difficulty: str | None = None,
                      genre: str | None = None,
                      domain: str | None = None) -> Dataset:
    rng = random.Random(seed)
    # Listening（Part1-4）は非対応のため既定はReadingのみ（5-7）
    part_list = parts or [5, 6, 7]

    generators = {
        1: gen_part1,
        2: gen_part2,
        3: gen_part3,
        4: gen_part4,
        5: gen_part5,
        6: gen_part6,
        7: gen_part7,
    }

    out_parts: List[PartBlock] = []
    for p in part_list:
        gen = generators.get(p)
        if gen and p in (5, 6, 7):  # 念のため5-7のみ
            if p == 7:
                out_parts.append(gen(per_part, rng, (p7_length or "short"), difficulty, genre, domain))
            elif p == 6:
                out_parts.append(gen(per_part, rng, difficulty, genre, domain))
            elif p == 5:
                out_parts.append(gen(per_part, rng, difficulty, genre, domain))

    today = _dt.date.today().isoformat()
    dataset: Dataset = {
        "title": title,
        "version": "1.0.0",
        "language": "en",
        "explanationsLanguage": "ja",
        "createdAt": today,
        "parts": out_parts,
        "metadata": {
            "noteJa": "このデータはスクリプトで自動生成されたオリジナル問題です（TOEIC形式に準拠）。"
        }
    }
    return dataset
