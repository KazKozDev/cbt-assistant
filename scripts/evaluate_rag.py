#!/usr/bin/env python3
"""Run the live retrieval benchmark against the configured Ollama embedding model."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.evaluation import score_evaluation  # noqa: E402
from src.rag.knowledge_base import SemanticRAG  # noqa: E402


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.46)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    cases = json.loads((PROJECT_ROOT / "evals/rag_retrieval.json").read_text())
    rag = SemanticRAG(
        PROJECT_ROOT / "knowledge_base",
        os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        os.getenv(
            "RAG_EMBED_MODEL",
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        ),
        cache_path=PROJECT_ROOT / "data/rag_eval_index.npz",
        trace_path=PROJECT_ROOT / "data/rag_eval_traces.jsonl",
        score_threshold=args.threshold,
    )
    await rag.load_and_embed()
    runs = [await rag.search(case["query"], args.top_k) for case in cases]
    report = {
        "index": rag.get_status(),
        "top_k": args.top_k,
        "metrics": score_evaluation(cases, runs),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
