"""Metrics for the versioned RAG retrieval evaluation set."""

from __future__ import annotations

from typing import Any


def matches_expected(chunk: dict[str, Any], case: dict[str, Any]) -> bool:
    source = case.get("expected_source")
    section = case.get("expected_section_contains")
    return (not source or chunk.get("source") == source) and (
        not section or section.casefold() in chunk.get("section_path", "").casefold()
    )


def score_evaluation(
    cases: list[dict[str, Any]], runs: list[list[dict[str, Any]]]
) -> dict[str, Any]:
    if len(cases) != len(runs):
        raise ValueError("cases and runs must have the same length")

    positive_count = 0
    recalled = 0
    reciprocal_rank_sum = 0.0
    negative_count = 0
    correct_abstentions = 0
    details = []

    for case, results in zip(cases, runs):
        is_negative = bool(case.get("expect_no_results"))
        if is_negative:
            negative_count += 1
            correct = not results
            correct_abstentions += int(correct)
            details.append({"id": case["id"], "passed": correct, "rank": None})
            continue

        positive_count += 1
        rank = next(
            (
                index
                for index, item in enumerate(results, start=1)
                if matches_expected(item["chunk"], case)
            ),
            None,
        )
        if rank is not None:
            recalled += 1
            reciprocal_rank_sum += 1.0 / rank
        details.append({"id": case["id"], "passed": rank is not None, "rank": rank})

    return {
        "case_count": len(cases),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "recall_at_k": round(recalled / positive_count, 4) if positive_count else None,
        "mrr": round(reciprocal_rank_sum / positive_count, 4)
        if positive_count
        else None,
        "abstention_accuracy": (
            round(correct_abstentions / negative_count, 4) if negative_count else None
        ),
        "details": details,
    }
