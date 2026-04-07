# Knockoff pipeline

This repository now includes a floating website bot backed by a retrieval service.
The bot answers from knockoff-related project documents and can optionally use an
OpenAI-compatible LLM API to synthesize grounded answers.

## Run locally

```bash
./scripts/run_portal.sh
```

Then open:

- `http://127.0.0.1:1313/`
- `http://127.0.0.1:1313/overview/`

## Deploy without your laptop

The website can stay on GitHub Pages, but the bot backend must run somewhere else.
This repository now supports that split deployment model:

- GitHub Pages serves the static Hugo site
- a separate backend service runs `backend/app.py`
- the site reads `BOT_API_URL` at build time

### Hugging Face Spaces backend

This repository includes a production container:

- `Dockerfile`
- `requirements.txt`

This repository is now set up to sync the bot backend to a Docker-based Hugging Face Space.

Files used for the Space deployment:

- `Dockerfile`
- `requirements.txt`
- `.github/workflows/hf-space.yaml`
- `space/README.md`

Required backend environment variables:

- `LLM_PROVIDER`
- provider key such as `GEMINI_API_KEY`
- optional `OPENAI_MODEL`
- optional `KNOCKOFF_BOT_SOURCES`

If you do not provide `KNOCKOFF_BOT_SOURCES`, the backend uses only this repository's
`content/`, which keeps the bot focused on the published site content.

### Hugging Face setup

1. Create a new Docker Space on Hugging Face.
2. Note the Space repo path, for example:

```text
your-username/knockoff-bot-api
```

3. In this GitHub repository, set:

- Actions variable: `HF_SPACE_REPO=your-username/knockoff-bot-api`
- Actions secret: `HF_TOKEN=...`

4. In the Hugging Face Space settings, add runtime secrets such as:

- `LLM_PROVIDER=gemini`
- `GEMINI_API_KEY=...`
- `OPENAI_MODEL=gemini-2.5-flash-lite`

5. Push to `main` or manually run `.github/workflows/hf-space.yaml`.

That workflow force-pushes a clean API-only bundle to the Space repository.

### GitHub Pages integration

The Pages workflow reads a repository variable named `BOT_API_URL`.
Set it to your deployed backend, for example:

```text
https://your-username-knockoff-bot-api.hf.space/api
```

Then push to `main` and the built site will point the floating bot at that remote API.
If `BOT_API_URL` is not set, the production Pages build disables the bot instead of
shipping a broken `localhost` endpoint.

## Enable Groq for summarized answers

The bot already supports OpenAI-compatible providers. Groq is the simplest option to
try first because it works with the existing `/chat/completions` integration.

1. Copy the example config:

```bash
cp .env.groq.example .env.local
```

2. Edit `.env.local` and set your real `GROQ_API_KEY`.

3. Start the site again:

```bash
./scripts/run_portal.sh
```

When Groq is enabled, `/api/health` will report:

- `llm.provider = "groq"`
- `llm.configured = true`

Default Groq settings used by this repo:

- `LLM_PROVIDER=groq`
- `OPENAI_BASE_URL=https://api.groq.com/openai/v1`
- `OPENAI_MODEL=llama-3.1-8b-instant`

## Use a local model with Ollama

If Groq is unstable, the simplest stable alternative is running a local model through
Ollama. This repo can talk to Ollama through its OpenAI-compatible endpoint, so no
frontend changes are needed.

1. Install Ollama and pull a model, for example:

```bash
ollama pull qwen2.5:3b
```

2. Copy the example config:

```bash
cp .env.ollama.example .env.local
```

3. Start the site:

```bash
./scripts/run_portal.sh
```

Expected health status:

- `llm.provider = "ollama"`
- `llm.configured = true`
- `llm.base_url = "http://127.0.0.1:11434/v1"`

This path removes third-party API instability, but answer quality and latency depend on
your local machine and chosen model.

## Use Gemini instead of local Ollama

If you want the bot to work without your laptop running, use a hosted provider.
Gemini is supported through its OpenAI-compatible endpoint.

```bash
cp .env.gemini.example .env.local
```

Then set a real `GEMINI_API_KEY` and deploy the backend container.

## Knowledge sources

By default the bot indexes:

- `content/`

Override them with `KNOCKOFF_BOT_SOURCES`, using `:` as the path separator on macOS or Linux.
