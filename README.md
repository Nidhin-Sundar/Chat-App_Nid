# Chat-App_Nid

A lightweight, local LLM chat app that streams responses from Ollama models via a FastAPI backend and a Streamlit frontend.

This project demonstrates a small, self-hosted chat UI that forwards user messages to a local Ollama model and streams the model's tokens back to the browser in real time.

## Contents

- `app.py` — Streamlit frontend (chat UI, model selection, streaming display)
- `backend.py` — FastAPI backend that forwards chat requests to Ollama and streams tokens through a `StreamingResponse`

## Features

- Local-first: uses your locally running Ollama instance (no cloud API keys required)
- Token-level streaming: the backend streams tokens from Ollama to the frontend for a responsive chat experience
- Simple and minimal: ready to run with a few commands

## Prerequisites

- Python 3.8+ (3.10+ recommended)
- pip (or a virtual environment you prefer)
- Ollama installed and `ollama serve` running with at least one model available (see Ollama docs)
- Recommended Python packages: `streamlit`, `fastapi`, `uvicorn`, `requests`, `pydantic`

If you don't have Ollama, follow instructions at https://ollama.com to install and start the service. The app expects Ollama's local HTTP API at `http://localhost:11434`.

## Quickstart

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install streamlit fastapi uvicorn requests pydantic
```

2. Make sure Ollama is running and a model is available:

```bash
# start ollama server (see Ollama docs; example)
ollama serve
# list models available locally
ollama list
```

3. Start the FastAPI backend (serves the streaming endpoint):

```bash
# from the project root
uvicorn backend:app --port 8000 --reload
```

4. Start the Streamlit frontend:

```bash
streamlit run app.py
```

5. Open the Streamlit URL printed in the terminal (usually `http://localhost:8501`) and start chatting.

## How it works (high level)

- The Streamlit app (`app.py`) provides a chat UI and auto-detects available Ollama models by running `ollama list`.
- When the user submits a message, the frontend sends the full conversation (list of messages) to the local FastAPI backend at `POST /chat`.
- The FastAPI backend (`backend.py`) forwards the conversation to Ollama's chat API at `http://localhost:11434/api/chat` with `stream: true`.
- The backend iterates the streaming lines from Ollama, extracts tokens, and yields them to the client using FastAPI's `StreamingResponse` with `text/plain`.
- The Streamlit frontend reads the streamed response and appends tokens to the chat message in real time, producing a responsive typing effect.

## API / Example request

The backend exposes a single endpoint:

- `POST /chat` — body: JSON with `model` and `messages`

Example payload (JSON):

```json
{
	"model": "llama3.2:latest",
	"messages": [
		{"role": "system", "content": "You are a helpful assistant."},
		{"role": "user", "content": "Hello!"}
	]
}
```

Example curl (non-streaming friendly but useful for testing connectivity):

```bash
curl -X POST http://localhost:8000/chat \
	-H "Content-Type: application/json" \
	-d '{"model":"llama3.2:latest","messages":[{"role":"user","content":"Hello"}]}'
```

For streaming tests you can use Python `requests` with `stream=True` (as the Streamlit frontend does).

## Implementation notes and caveats

- The project assumes Ollama's HTTP API is available at `http://localhost:11434` (default). If your Ollama is bound to a different host/port, update `backend.py` accordingly.
- `app.py` uses `subprocess.run(['ollama', 'list'])` to detect models. If `ollama` is not on PATH or unavailable, it falls back to `llama3.2:latest`.
- The backend currently streams raw token content as `text/plain`. If you need JSON events or SSE, adjust `backend.py` to format events accordingly.
- No authentication, CORS or rate-limiting is implemented. For any public deployment, add proper security controls.

## Troubleshooting

- Backend not running / connection refused: ensure the backend is started with `uvicorn backend:app --port 8000` and that it reports no errors.
- Ollama not running / slow responses: ensure `ollama serve` is running. If Ollama is slow to respond, increase the timeout in `app.py` or investigate the model resource usage locally.
- `ollama` command not found when selecting models: either install Ollama CLI or set a model name manually in the Streamlit UI.
- Stream shows nothing or stalls: check backend logs for exceptions. The backend prints raw request errors to the console if Ollama returns non-streaming responses.



