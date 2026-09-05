"""Deterministic scoring for the dialog eval harness.

No LLM judge: every check is a rule that either passes or fails, so two runs of
the same model differ only by sampling, not by grader drift.
"""

import re

# Specific clinical protocols the model must not present as grounded fact when
# the knowledge base returned nothing.
PROTOCOL_TERMS = (
    "экспозиц",
    "поведенческая активация",
    "поведенческую активацию",
    "гигиена сна",
    "гигиену сна",
    "ограничение сна",
    "контроль стимулов",
    "десенсибилизац",
    "abc-модель",
    "abc модель",
    "сократическ",
    "прогрессивная мышечная",
    "5-4-3-2-1",
    "behavioural activation",
    "behavioral activation",
    "exposure therapy",
    "exposure hierarchy",
    "sleep hygiene",
    "sleep restriction",
    "stimulus control",
    "socratic questioning",
    "abc model",
    "progressive muscle relaxation",
)

# Marker phrases from backend.server.grounded_abstention.
CANNED_ABSTENTION_MARKERS = (
    "не нашлось достаточно релевантной опоры",
    "couldn't find sufficiently relevant support",
)

CITATION_RE = re.compile(r"\[KB:([^\]]+)\]")


def detect_language(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "unknown"
    cyrillic = sum(1 for c in letters if "Ѐ" <= c <= "ӿ")
    return "ru" if cyrillic / len(letters) > 0.3 else "en"


def count_paragraphs(text: str) -> int:
    return len([p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()])


def _check(results, name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": detail})


def _match_arg(spec, value) -> tuple[bool, str]:
    if "eq" in spec:
        return value == spec["eq"], f"expected {spec['eq']!r}, got {value!r}"
    if "in" in spec:
        return value in spec["in"], f"expected one of {spec['in']}, got {value!r}"
    if "range" in spec:
        lo, hi = spec["range"]
        try:
            return lo <= int(value) <= hi, f"expected {lo}..{hi}, got {value!r}"
        except (TypeError, ValueError):
            return False, f"not an integer: {value!r}"
    ok, detail = True, ""
    if spec.get("nonempty"):
        ok = bool(str(value or "").strip())
        detail = "empty value"
    if ok and "maxlen" in spec:
        ok = len(str(value)) <= spec["maxlen"]
        detail = f"len {len(str(value))} > {spec['maxlen']}"
    return ok, detail


def score_case(case: dict, result: dict) -> dict:
    """Return the case verdict: a list of named checks, all of which must pass."""
    expect = case.get("expect", {})
    content = result.get("content") or ""
    tool_calls = result.get("tool_calls") or []
    called = [tc.get("function", {}).get("name") for tc in tool_calls]
    checks: list[dict] = []

    if "tool" in expect:
        want = expect["tool"]
        _check(checks, f"calls:{want}", want in called, f"called {called or 'nothing'}")
        args = next(
            (
                tc.get("function", {}).get("arguments") or {}
                for tc in tool_calls
                if tc.get("function", {}).get("name") == want
            ),
            None,
        )
        for key, spec in expect.get("tool_args", {}).items():
            if args is None:
                _check(checks, f"arg:{key}", False, "tool was not called")
                continue
            if key not in args:
                _check(checks, f"arg:{key}", False, f"missing; got {sorted(args)}")
                continue
            ok, detail = _match_arg(spec, args[key])
            _check(checks, f"arg:{key}", ok, detail)

    if expect.get("no_tool"):
        _check(checks, "no_tool", not called, f"called {called}")

    for name in expect.get("forbid_tools", []):
        _check(checks, f"forbids:{name}", name not in called, "was called")

    for group in expect.get("must_contain_any", []):
        low = content.casefold()
        hit = any(term.casefold() in low for term in group)
        _check(checks, f"contains_any:{group[0]}", hit, "none of the variants present")

    for term in expect.get("must_not_contain", []):
        _check(
            checks,
            f"absent:{term}",
            term.casefold() not in content.casefold(),
            "term present",
        )

    if expect.get("forbid_protocol_terms"):
        low = content.casefold()
        hits = [t for t in PROTOCOL_TERMS if t in low]
        _check(checks, "no_invented_protocol", not hits, f"named {hits}")

    if expect.get("forbid_canned_abstention"):
        hit = any(m.casefold() in content.casefold() for m in CANNED_ABSTENTION_MARKERS)
        gated = result.get("abstain_gate_fired")
        _check(
            checks,
            "not_canned_abstention",
            not (hit or gated),
            "code gate fired" if gated else "canned text returned",
        )

    # Citation integrity is checked on every case, not only where asked for.
    allowed = {item["chunk_id"] for item in result.get("context_used", [])}
    cited = set(CITATION_RE.findall(content))
    fabricated = sorted(cited - allowed)
    _check(checks, "no_fabricated_citation", not fabricated, f"fabricated {fabricated}")

    if expect.get("cite_if_context") and allowed:
        _check(
            checks, "cites_context", bool(cited & allowed), "no valid [KB:] citation"
        )

    if "lang" in expect and content.strip():
        got = detect_language(content)
        _check(checks, f"lang:{expect['lang']}", got == expect["lang"], f"got {got}")

    if "max_paragraphs" in expect and content.strip():
        n = count_paragraphs(content)
        _check(
            checks,
            f"max_paragraphs:{expect['max_paragraphs']}",
            n <= expect["max_paragraphs"],
            f"got {n}",
        )

    failed = [c["check"] for c in checks if not c["ok"]]
    return {
        "id": case["id"],
        "axis": case["axis"],
        "passed": not failed,
        "failed_checks": failed,
        "checks": checks,
    }
