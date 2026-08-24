# Contributing

Thanks for contributing to CBT Assistant.

## Before You Start

- Open an issue first for substantial changes so scope and direction are aligned before implementation.
- Keep changes focused. Small, reviewable pull requests are preferred over large mixed refactors.
- If your change affects behavior, add or update tests when practical.

## Local Setup

```bash
git clone https://github.com/KazKozDev/cbt-assistant.git
cd cbt-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start Ollama and pull the required models:

```bash
ollama serve
ollama pull ornith-1.5:9b
ollama pull qwen3-embedding:4b
```

Run the app:

```bash
python backend/server.py
```

Run tests:

```bash
pytest
```

## Contribution Areas

- Clinical knowledge base quality and structure in `knowledge_base/`
- Memory, recommendation, and prompt behavior
- Frontend UX, accessibility, responsiveness, and localization
- Journaling, assessments, reports, and data flows
- Safety behavior and crisis-adjacent guardrails
- Documentation and local developer setup

## Pull Requests

- Describe what changed and why.
- Link the related issue when one exists.
- Include screenshots for UI changes when helpful.
- Mention any manual verification steps.

## Scope Notes

- Avoid committing personal data, local databases, or `.env` files.
- Do not introduce hosted-model assumptions into flows designed to run locally.
- Keep clinical or mental-health claims conservative and grounded in the repository's documented approach.
