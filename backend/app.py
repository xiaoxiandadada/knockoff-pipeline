from __future__ import annotations

import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.llm import generate_answer
from backend.rag import KnowledgeBase, collect_source_files, display_source_path
from backend.settings import ROOT_DIR, get_llm_settings, knowledge_paths


RUNTIME_DIR = ROOT_DIR / "runtime" / "bot"
kb = KnowledgeBase(RUNTIME_DIR)
app = FastAPI(title="Knockoff Bot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=2)
    top_k: int = Field(default=4, ge=1, le=8)
    use_llm: bool = True


def ensure_index() -> dict[str, int]:
    payload = kb.load()
    if payload.get("chunks"):
        return {"documents": len(payload.get("documents", [])), "chunks": len(payload.get("chunks", []))}

    files = collect_source_files(knowledge_paths())
    return kb.ingest_paths(files)


@app.on_event("startup")
def startup() -> None:
    ensure_index()


@app.get("/api/health")
def health() -> dict:
    llm = get_llm_settings()
    payload = kb.load()
    return {
        "status": "ok",
        "documents": len(payload.get("documents", [])),
        "chunks": len(payload.get("chunks", [])),
        "llm": {
            "provider": llm.provider,
            "configured": llm.configured,
            "model": llm.model,
            "base_url": llm.base_url,
        },
    }


@app.post("/api/reindex")
def reindex() -> dict:
    files = collect_source_files(knowledge_paths())
    summary = kb.ingest_paths(files)
    return {"status": "ok", "summary": summary, "files": [str(path) for path in files]}


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict:
    ensure_index()
    retrieval = kb.answer_extractively(payload.question, top_k=payload.top_k)
    for citation in retrieval.get("citations", []):
        citation["source_path"] = display_source_path(citation.get("source_path", ""))
    for match in retrieval.get("matches", []):
        match["source_path"] = display_source_path(match.get("source_path", ""))

    if not payload.use_llm or not retrieval["matches"]:
        return retrieval

    llm = get_llm_settings()
    if not llm.configured:
        retrieval["warning"] = (
            f"LLM provider '{llm.provider}' is not configured. "
            "Set the provider API key, for example GROQ_API_KEY, to enable synthesized answers."
        )
        retrieval["mode"] = "extractive_fallback"
        return retrieval

    try:
        retrieval["answer"] = generate_answer(payload.question, retrieval["matches"], llm)
        retrieval["mode"] = "llm"
        return retrieval
    except Exception as exc:
        retrieval["warning"] = f"LLM call failed, using retrieval fallback: {exc}"
        retrieval["mode"] = "extractive_fallback"
        return retrieval
