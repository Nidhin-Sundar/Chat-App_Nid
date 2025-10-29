from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[Message]

@app.post("/chat")
def chat(request: ChatRequest):
    # Forward to Ollama
    ollama_payload = {
        "model": request.model,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "stream": True
    }

    def stream():
        with requests.post("http://localhost:11434/api/chat", json=ollama_payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token

    return StreamingResponse(stream(), media_type="text/plain")