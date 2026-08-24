from src.rag.evaluation import score_evaluation


def result(source: str, section: str):
    return {"chunk": {"source": source, "section_path": section}, "score": 0.8}


def test_retrieval_metrics_cover_recall_rank_and_abstention():
    cases = [
        {"id": "a", "expected_source": "a.md", "expected_section_contains": "Target"},
        {"id": "b", "expected_source": "b.md", "expected_section_contains": "Needle"},
        {"id": "negative", "expect_no_results": True},
    ]
    runs = [
        [result("a.md", "Target")],
        [result("x.md", "Other"), result("b.md", "Needle")],
        [],
    ]
    metrics = score_evaluation(cases, runs)
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 0.75
    assert metrics["abstention_accuracy"] == 1.0
