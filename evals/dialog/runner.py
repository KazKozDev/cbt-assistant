"""Run the dialog eval suite against an Ollama model.

Reuses the production prompt assembly, tool schema and retrieval gate from
backend.server, so the harness measures the model as the app actually drives it.

    python evals/dialog/runner.py --model qwen3.5:9b
    python evals/dialog/runner.py --model qwen3.6:27b --out evals/dialog/reports
    python evals/dialog/runner.py --model qwen3.5:4b --axis safety
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

import backend.server as S  # noqa: E402
from src.llm.ollama_client import OllamaClient  # noqa: E402
from scoring import score_case  # noqa: E402

CASES_PATH = Path(__file__).parent / "cases.jsonl"
DEFAULT_OUT = Path(__file__).parent / "reports"
MAX_TOOL_ROUNDS = 2

# Neutral stand-ins so a tool round can complete without touching the real DB.
TOOL_STUBS = {
    "get_user_sleep_history": '{"records": []}',
    "get_user_test_results": '{"results": []}',
    "get_user_activities": '{"activities": []}',
    "add_user_activity": "Activity added.",
    "start_sos_exercise": "SOS portal opened.",
    "recommend_test": "Test dialog opened.",
    "add_thought_record": "Thought record #1 saved to diary.",
    "add_sleep_diary_record": "Sleep record #1 saved to sleep diary.",
}


def load_cases(axis: str | None, limit: int | None) -> list[dict]:
    cases = [
        json.loads(line)
        for line in CASES_PATH.read_text("utf-8").splitlines()
        if line.strip()
    ]
    if axis:
        cases = [c for c in cases if c["axis"] == axis]
    return cases[:limit] if limit else cases


async def build_messages(case: dict) -> tuple[list[dict], list[dict], bool]:
    """Mirror backend.server.prepare_chat_messages for a stateless eval turn."""
    message, language = case["message"], case.get("lang", "ru")
    if case.get("retrieval", "natural") == "force_empty":
        context, status = [], "no_relevant_context"
        context_used = []
    else:
        retrieval = await S.kb.search_with_trace(message, top_k=3)
        context = retrieval["results"]
        status = retrieval["trace"]["status"]
        context_used = S.serialize_rag_context(context, retrieval["trace"])
    gate_fired = not context and S.requires_grounded_clinical_answer(message)

    system_prompt = S.prompt_manager.build_system_prompt(
        context, None, None, None, retrieval_status=status, profile_memory=None
    )
    system_prompt = f"{system_prompt}\n\n{S.build_language_instruction(language)}"
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(case.get("history", []))
    messages.append({"role": "user", "content": message})
    return messages, context_used, gate_fired


async def run_case(client: OllamaClient, case: dict) -> dict:
    started = time.perf_counter()
    messages, context_used, gate_fired = await build_messages(case)

    # The server short-circuits to canned text here without consulting the model.
    if gate_fired:
        return {
            "content": S.grounded_abstention(case.get("lang", "ru")),
            "tool_calls": [],
            "context_used": context_used,
            "abstain_gate_fired": True,
            "latency_ms": round((time.perf_counter() - started) * 1000),
        }

    all_tool_calls: list[dict] = []
    content = ""
    for _ in range(MAX_TOOL_ROUNDS):
        resp = await client.chat(
            messages, options=S.LLM_OPTIONS, tools=S.get_user_data_tools()
        )
        content = resp.get("content", "") or ""
        tool_calls = resp.get("tool_calls") or []
        if not tool_calls:
            break
        all_tool_calls.extend(tool_calls)
        messages.append(
            {"role": "assistant", "content": content, "tool_calls": tool_calls}
        )
        for tc in tool_calls:
            name = tc.get("function", {}).get("name", "")
            messages.append(
                {
                    "role": "tool",
                    "name": name,
                    "content": TOOL_STUBS.get(name, f"Error: Unknown tool {name}"),
                }
            )
    return {
        "content": content,
        "tool_calls": all_tool_calls,
        "context_used": context_used,
        "abstain_gate_fired": False,
        "latency_ms": round((time.perf_counter() - started) * 1000),
    }


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=S.DEFAULT_OLLAMA_MODEL)
    parser.add_argument("--axis", choices=["tool_calling", "safety", "abstention"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--verbose", action="store_true", help="print every failure detail"
    )
    args = parser.parse_args()

    cases = load_cases(args.axis, args.limit)
    print("Loading knowledge base index...", flush=True)
    await S.kb.load_and_embed()
    client = OllamaClient(S.OLLAMA_BASE_URL, args.model)
    print(f"Running {len(cases)} cases against {args.model}\n", flush=True)

    semaphore = asyncio.Semaphore(args.concurrency)
    done = 0

    async def worker(case: dict) -> dict:
        nonlocal done
        async with semaphore:
            try:
                result = await run_case(client, case)
            except (
                Exception
            ) as exc:  # a transport failure is a failed case, not a crash
                result = {
                    "content": "",
                    "tool_calls": [],
                    "context_used": [],
                    "abstain_gate_fired": False,
                    "latency_ms": 0,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            verdict = score_case(case, result)
            verdict["latency_ms"] = result["latency_ms"]
            verdict["abstain_gate_fired"] = result["abstain_gate_fired"]
            verdict["response"] = result["content"]
            verdict["called_tools"] = [
                tc.get("function", {}).get("name") for tc in result["tool_calls"]
            ]
            if "error" in result:
                verdict["error"] = result["error"]
            done += 1
            mark = "." if verdict["passed"] else "F"
            print(
                f"{mark}",
                end="" if done % 60 else f" {done}/{len(cases)}\n",
                flush=True,
            )
            return verdict

    verdicts = await asyncio.gather(*(worker(c) for c in cases))
    print("\n")

    by_axis: dict[str, list[dict]] = {}
    for v in verdicts:
        by_axis.setdefault(v["axis"], []).append(v)

    print(f"{'axis':<14}{'pass':>6}{'total':>7}{'rate':>8}")
    for axis in sorted(by_axis):
        group = by_axis[axis]
        ok = sum(1 for v in group if v["passed"])
        print(f"{axis:<14}{ok:>6}{len(group):>7}{ok / len(group):>7.0%}")
    total_ok = sum(1 for v in verdicts if v["passed"])
    print(
        f"{'OVERALL':<14}{total_ok:>6}{len(verdicts):>7}{total_ok / len(verdicts):>7.0%}"
    )

    gated = [v for v in verdicts if v["abstain_gate_fired"]]
    if gated:
        print(f"\ncode abstention gate fired on {len(gated)} cases (model never ran):")
        for v in gated:
            print(f"  {'FAIL' if not v['passed'] else 'ok  '} {v['id']}")

    failures = [v for v in verdicts if not v["passed"]]
    if failures:
        print(f"\n{len(failures)} failures:")
        for v in failures:
            print(f"  {v['id']:<24} {', '.join(v['failed_checks'])}")
            if args.verbose:
                for c in v["checks"]:
                    if not c["ok"]:
                        print(f"      {c['check']}: {c['detail']}")
                print(f"      response: {v['response'][:300]!r}\n")

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = (
        args.out / f"{args.model.replace(':', '_').replace('/', '_')}-{stamp}.json"
    )
    report_path.write_text(
        json.dumps(
            {
                "model": args.model,
                "timestamp": stamp,
                "index_version": S.kb.index_version,
                "options": S.LLM_OPTIONS,
                "totals": {
                    axis: {
                        "passed": sum(1 for v in g if v["passed"]),
                        "total": len(g),
                    }
                    for axis, g in by_axis.items()
                },
                "cases": verdicts,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nreport: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
