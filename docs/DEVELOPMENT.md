# Development and evaluation

## Local setup

Install Python 3.10+ and Ollama, then run:

```bash
git clone https://github.com/KazKozDev/cbt-assistant.git
cd cbt-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen3.5:9b
ollama pull qwen3-embedding:4b
python backend/server.py
```

Open `http://localhost:8000`. Start `ollama serve` in another terminal first if the Ollama service is not already running.

The macOS and Windows launchers use `uv` to install a local Python 3.12 environment when needed, install dependencies, prepare Ollama, download the models, release port `8000`, wait for the application health check, and open the browser. Linux currently uses the manual setup.

## Deterministic tests

Run the suite without the live model-backed memory test:

```bash
python -m pytest -q --ignore=tests/test_real_memory.py
```

The current suite passes 51 tests. It covers SQLite behavior, prompt construction, structural chunking, cache restoration, fail-closed indexing, thresholds, provenance, retrieval metrics, API endpoints, and application-tool execution.

## Retrieval evaluation

Run the versioned retrieval cases with FastEmbed:

```bash
python scripts/evaluate_rag.py --top-k 3 --threshold 0.46 --output data/rag_eval_report.json
```

The cases are stored in `evals/rag_retrieval.json`. The checked-in baseline (`evals/rag_baseline.json`) contains 18 Russian, English, and off-topic cases. With `paraphrase-multilingual-mpnet-base-v2`, it records Recall@3 `0.8571`, MRR `0.7024`, and abstention accuracy `1.0`.

This small regression set measures retrieval behavior, not clinical correctness. Re-run it after changing the embedding model, relevance threshold, chunking logic, or knowledge content.

## Live checks

Run the model-backed memory integration when Ollama and the selected chat model are available:

```bash
python -m pytest tests/test_real_memory.py -s
```

`tests/test_real_interaction.py` is a manual end-to-end script for an already running application. Passing software checks does not validate the clinical quality of generated responses.

## Contributing

Read [CONTRIBUTING.md](../CONTRIBUTING.md) before a substantial pull request. Keep changes focused, update tests when behavior changes, and include screenshots for relevant UI work. Report security-sensitive problems through [SECURITY.md](../SECURITY.md).
