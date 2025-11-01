from __future__ import annotations

import argparse
import json
import os
import random
from typing import Any, Dict, List, Optional

from toeic_generator import generate_dataset


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_dataset(pattern: str) -> Dict[str, Any]:
    """Load pattern1.json or pattern2.json as UTF-8 JSON.

    Args:
        pattern: "pattern1" or "pattern2"
    Returns:
        Parsed JSON as dict
    Raises:
        FileNotFoundError, json.JSONDecodeError
    """
    filename = f"{pattern}.json"
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def derive_stem(q: Dict[str, Any]) -> str:
    """Derive a displayable stem for various TOEIC parts."""
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


def print_context_extras(q: Dict[str, Any]) -> None:
    """Print extra context like conversations for Part 3, if present."""
    ctx = q.get("context") or {}
    conversation = ctx.get("conversation")
    if isinstance(conversation, list):
        for turn in conversation:
            sp = turn.get("speaker", "?")
            text = turn.get("text", "")
            print(f"{sp}: {text}")


def collect_questions(data: Dict[str, Any], part: Optional[int]) -> List[Dict[str, Any]]:
    """Collect questions from a specific part or all parts."""
    questions: List[Dict[str, Any]] = []
    for p in data.get("parts", []):
        if part is None or p.get("part") == part:
            for q in p.get("questions", []):
                # enrich with part metadata for later display
                q_copy = dict(q)
                q_copy["_part"] = p.get("part")
                q_copy["_part_name"] = p.get("name")
                questions.append(q_copy)
    return questions


def interactive_quiz(questions: List[Dict[str, Any]], limit: int) -> None:
    """Run an interactive quiz in the terminal."""
    total = min(limit, len(questions)) if limit > 0 else len(questions)
    score = 0
    for idx, q in enumerate(questions[:total], start=1):
        print("\n" + "=" * 70)
        print(f"[{idx}/{total}] Part {q.get('_part')}: {q.get('_part_name')}")
        stem = derive_stem(q)
        print(stem)
        print_context_extras(q)

        options: List[str] = q.get("options", [])
        for opt in options:
            print(opt)

        # Expect user to input A/B/C/D (or a/b/...).
        valid_letters = [chr(ord('A') + i) for i in range(len(options))]
        while True:
            raw = input(f"Your answer ({'/'.join(valid_letters)}): ").strip().upper()
            if raw in valid_letters:
                break
            print("無効な入力です。もう一度 A/B/C/D 等の選択肢の文字で入力してください。")

        is_correct = raw == q.get("answer")
        if is_correct:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Incorrect. Correct answer: {q.get('answer')}")
        explanation = q.get("explanationJa")
        if explanation:
            print(f"解説: {explanation}")

    print("\n" + "-" * 70)
    print(f"Score: {score}/{total} ({round(100*score/total) if total else 0}%)")


def preview_questions(questions: List[Dict[str, Any]], limit: int) -> None:
    """Print questions with answers for quick preview (no user input)."""
    total = min(limit, len(questions)) if limit > 0 else len(questions)
    for idx, q in enumerate(questions[:total], start=1):
        print("\n" + "=" * 70)
        print(f"[{idx}/{total}] Part {q.get('_part')}: {q.get('_part_name')}")
        stem = derive_stem(q)
        print(stem)
        print_context_extras(q)
        for opt in q.get("options", []):
            print(opt)
        print(f"Answer: {q.get('answer')}")
        if q.get("explanationJa"):
            print(f"解説: {q.get('explanationJa')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TOEIC Mock Test runner")
    parser.add_argument(
        "--source",
        choices=["static", "generated"],
        default="static",
        help="static: data/pattern*.json を使用 / generated: スクリプトで問題を自動生成",
    )
    parser.add_argument(
        "--pattern",
        choices=["pattern1", "pattern2"],
        default="pattern2",
        help="Use pattern1 (各Part×5問) or pattern2 (ミニ10問)",
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "preview"],
        default="preview",
        help="interactive: 回答を入力して採点 / preview: 問題と正解を流し見",
    )
    parser.add_argument(
        "--part",
        type=int,
        default=None,
        help="Part番号を指定（1..7）。未指定なら全Partから出題",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="出題/表示する問題数（上限）",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="出題順をシャッフル",
    )
    # 生成モード向け
    parser.add_argument(
        "--gen-per-part",
        type=int,
        default=3,
        help="generated ソース時: Partごとに生成する問題数（既定: 3）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="生成の再現性を担保する乱数シード（同じseedで同じ問題が生成）",
    )
    parser.add_argument(
        "--write",
        type=str,
        default=None,
        help="generated ソース時: 生成したデータをJSONで保存するパス",
    )

    args = parser.parse_args()

    # Listening（Part1-4）を非対応にする: ユーザーが明示的に1-4を指定した場合は警告して終了
    if args.part is not None and args.part < 5:
        print("Listening（Part1-4）は現在無効化しています。Part 5〜7 を指定してください。")
        return

    if args.source == "generated":
        # 生成データ作成
        parts = [args.part] if args.part else None
        data = generate_dataset(
            title="TOEIC Mock Test - Generated",
            per_part=args.gen_per_part,
            parts=parts,
            seed=args.seed,
        )
        # 必要なら保存
        if args.write:
            try:
                with open(args.write, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"生成データを書き出しました: {args.write}")
            except OSError as e:
                print(f"生成データの書き出しに失敗しました: {e}")
    else:
        try:
            data = load_dataset(args.pattern)
        except FileNotFoundError:
            print(f"データファイルが見つかりません: {DATA_DIR} / {args.pattern}.json")
            return
        except json.JSONDecodeError as e:
            print(f"JSONの読み込みに失敗しました: {e}")
            return

    # 静的/生成を問わず、Listening（Part1-4）はフィルタして除外
    if isinstance(data, dict):
        parts_only_reading: List[Dict[str, Any]] = []
        for p in data.get("parts", []):
            try:
                if int(p.get("part")) >= 5:
                    parts_only_reading.append(p)
            except Exception:
                # part番号が不正なら無視
                pass
        data["parts"] = parts_only_reading

    qs = collect_questions(data, args.part)
    if not qs:
        print("該当する問題がありません（Part指定が厳しすぎる可能性があります）。")
        return
    if args.shuffle:
        random.shuffle(qs)

    if args.mode == "interactive":
        interactive_quiz(qs, args.count)
    else:
        preview_questions(qs, args.count)


if __name__ == "__main__":
    main()
