import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

from dotenv import load_dotenv
from google import genai

load_dotenv()


INITIAL_PROMPT = """
You are an assistant that converts meeting notes into structured action items.

Return the output as valid JSON with exactly these top-level keys:
- decisions
- action_items
- open_questions

Expected JSON schema:
{
  "decisions": ["..."],
  "action_items": [
    {
      "task": "...",
      "owner": "...",
      "deadline": "..."
    }
  ],
  "open_questions": ["..."]
}
""".strip()


REVISION_1_PROMPT = """
You are an assistant that converts meeting notes into structured action items.

Return the output as valid JSON with exactly these top-level keys:
- decisions
- action_items
- open_questions

Rules:
1. Extract only information explicitly supported by the notes.
2. Separate decisions from action items.
3. For each action item, include:
   - task
   - owner
   - deadline
4. If owner is missing, use "Not specified".
5. If deadline is missing, use "Not specified".
6. If there are no action items, return an empty list.

Expected JSON schema:
{
  "decisions": ["..."],
  "action_items": [
    {
      "task": "...",
      "owner": "...",
      "deadline": "..."
    }
  ],
  "open_questions": ["..."]
}
""".strip()


REVISION_2_PROMPT = """
You are an assistant that converts meeting notes into structured action items.

Return the output as valid JSON with exactly these top-level keys:
- decisions
- action_items
- open_questions

Rules:
1. Extract only facts explicitly stated in the meeting notes.
2. Do not invent decisions, tasks, owners, or deadlines.
3. Separate confirmed decisions from tentative ideas.
4. Treat uncertain or tentative statements as open_questions unless the notes clearly confirm a decision or task.
5. For each action item, include:
   - task
   - owner
   - deadline
6. If owner is missing, use "Not specified".
7. If deadline is missing, use "Not specified".
8. If there are no action items, return an empty list.
9. Keep the output concise and faithful to the notes.
10. Return valid JSON only. Do not add markdown fences or extra commentary.

Expected JSON schema:
{
  "decisions": ["..."],
  "action_items": [
    {
      "task": "...",
      "owner": "...",
      "deadline": "..."
    }
  ],
  "open_questions": ["..."]
}
""".strip()


PROMPTS = {
    "initial": INITIAL_PROMPT,
    "revision1": REVISION_1_PROMPT,
    "revision2": REVISION_2_PROMPT,
}


def load_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing GEMINI_API_KEY. Add it to your local .env file or set it as an environment variable."
        )
    return api_key


def get_client() -> genai.Client:
    return genai.Client(api_key=load_api_key())


def clean_model_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def call_gemini(notes: str, prompt_name: str, model_name: str) -> str:
    client = get_client()
    prompt = PROMPTS[prompt_name]

    response = client.models.generate_content(
        model=model_name,
        contents=f"{prompt}\n\nMeeting notes:\n{notes}"
    )

    return clean_model_text(response.text)


def try_parse_json(text: str) -> Optional[Dict]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def ensure_output_dir(output_dir: str) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_case_output(
    case_id: str,
    prompt_name: str,
    notes: str,
    raw_output: str,
    output_dir: str,
    expected_output: Optional[str] = None
) -> None:
    out_dir = ensure_output_dir(output_dir)
    parsed = try_parse_json(raw_output)

    payload = {
        "case_id": case_id,
        "prompt_version": prompt_name,
        "input_notes": notes,
        "expected_output_note": expected_output,
        "model_output_raw": raw_output,
        "model_output_json": parsed,
    }

    file_path = out_dir / f"{case_id}_{prompt_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def print_structured_output(
    case_id: str,
    notes: str,
    raw_output: str,
    expected_output: Optional[str] = None
) -> None:
    print("\n" + "=" * 60)
    print(f"CASE: {case_id}")
    print("=" * 60)

    print("\n=== INPUT NOTES ===")
    print(notes)

    if expected_output:
        print("\n=== EXPECTED OUTPUT NOTE ===")
        print(expected_output)

    print("\n=== MODEL OUTPUT ===")
    print(raw_output)


def parse_eval_set_md(file_path: str) -> List[Dict[str, str]]:
    text = Path(file_path).read_text(encoding="utf-8")

    case_pattern = re.compile(
        r"##\s*(Case\s+\d+:[^\n]+)\s*"
        r"(.*?)(?=\n##\s*Case\s+\d+:|\Z)",
        re.DOTALL
    )
    input_pattern = re.compile(
        r"###\s*Input\s*(.*?)(?=\n###\s*Expected Output|\Z)",
        re.DOTALL
    )
    expected_pattern = re.compile(
        r"###\s*Expected Output\s*(.*?)(?=\Z)",
        re.DOTALL
    )

    cases: List[Dict[str, str]] = []

    for idx, match in enumerate(case_pattern.finditer(text), start=1):
        case_title = match.group(1).strip()
        body = match.group(2).strip()

        input_match = input_pattern.search(body)
        expected_match = expected_pattern.search(body)

        if not input_match:
            continue

        input_text = input_match.group(1).strip()
        expected_text = expected_match.group(1).strip() if expected_match else ""

        case_id = f"case_{idx}"
        cases.append(
            {
                "case_id": case_id,
                "case_title": case_title,
                "input": input_text,
                "expected_output": expected_text,
            }
        )

    if not cases:
        raise ValueError(
            f"No cases were parsed from {file_path}. "
            f"Check that the markdown uses '## Case', '### Input', and '### Expected Output'."
        )

    return cases


def run_single_case(
    prompt_name: str,
    model_name: str,
    output_dir: str,
    notes_file: Optional[str] = None
) -> None:
    if notes_file:
        notes = Path(notes_file).read_text(encoding="utf-8")
        case_id = Path(notes_file).stem
    else:
        notes = """
Discussed launching the new marketing campaign in May.
Sarah will prepare the first campaign draft by next Monday.
The team agreed to increase the campaign budget by 10%.
There was also some uncertainty about whether the pricing page needs revision.
""".strip()
        case_id = "sample_case"

    raw_output = call_gemini(notes, prompt_name, model_name)
    print_structured_output(case_id=case_id, notes=notes, raw_output=raw_output)
    save_case_output(
        case_id=case_id,
        prompt_name=prompt_name,
        notes=notes,
        raw_output=raw_output,
        output_dir=output_dir,
        expected_output=None,
    )

    print(f"\nSaved output to {Path(output_dir) / f'{case_id}_{prompt_name}.json'}")


def run_eval_set(
    eval_file: str,
    prompt_name: str,
    model_name: str,
    output_dir: str
) -> None:
    cases = parse_eval_set_md(eval_file)

    print(f"\nLoaded {len(cases)} cases from {eval_file}")
    print(f"Prompt version: {prompt_name}")
    print(f"Model: {model_name}")

    summary = []

    for case in cases:
        case_id = case["case_id"]
        case_title = case["case_title"]
        notes = case["input"]
        expected = case["expected_output"]

        print("\n" + "#" * 60)
        print(f"RUNNING {case_id}: {case_title}")
        print("#" * 60)

        raw_output = call_gemini(notes, prompt_name, model_name)

        print_structured_output(
            case_id=case_id,
            notes=notes,
            raw_output=raw_output,
            expected_output=expected
        )

        save_case_output(
            case_id=case_id,
            prompt_name=prompt_name,
            notes=notes,
            raw_output=raw_output,
            output_dir=output_dir,
            expected_output=expected,
        )

        summary.append(
            {
                "case_id": case_id,
                "case_title": case_title,
                "output_file": str(Path(output_dir) / f"{case_id}_{prompt_name}.json")
            }
        )

    summary_file = Path(output_dir) / f"summary_{prompt_name}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("EVALUATION RUN COMPLETE")
    print("=" * 60)
    print(f"Saved per-case outputs to: {Path(output_dir).resolve()}")
    print(f"Saved summary file to: {summary_file.resolve()}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize meeting notes into action items using Gemini."
    )

    parser.add_argument(
        "--mode",
        choices=["single", "eval"],
        default="single",
        help="single: run one sample or one notes file; eval: run all cases in eval_set.md"
    )
    parser.add_argument(
        "--prompt",
        choices=["initial", "revision1", "revision2"],
        default="revision2",
        help="Prompt version to use"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model name"
    )
    parser.add_argument(
        "--notes-file",
        default=None,
        help="Path to a local notes text file for single mode"
    )
    parser.add_argument(
        "--eval-file",
        default="eval_set.md",
        help="Path to eval_set.md"
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory to save output files"
    )

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.prompt not in PROMPTS:
        raise ValueError(f"Unknown prompt version: {args.prompt}")

    if args.mode == "single":
        run_single_case(
            prompt_name=args.prompt,
            model_name=args.model,
            output_dir=args.output_dir,
            notes_file=args.notes_file
        )
    else:
        run_eval_set(
            eval_file=args.eval_file,
            prompt_name=args.prompt,
            model_name=args.model,
            output_dir=args.output_dir
        )


if __name__ == "__main__":
    main()