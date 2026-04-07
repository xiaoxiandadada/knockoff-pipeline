from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import pathlib
import re
from collections import Counter
from math import log
from typing import Any, Iterable


TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".rst", ".py", ".R"}


@dataclasses.dataclass
class ParsedDocument:
    title: str
    source_path: str
    text: str


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat()


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.+?```", " ", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"[*_>-]+", " ", text)
    return normalize_whitespace(text)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]{2,}|[\u4e00-\u9fff]", text.lower())


def detect_question_language(text: str) -> str:
    return "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"


def source_language(source_path: str) -> str:
    normalized = source_path.replace("\\", "/").lower()
    if "/content/zh/" in normalized:
        return "zh"
    return "en"


def parse_path(path: pathlib.Path) -> ParsedDocument:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() in {".md", ".markdown", ".rst"}:
        text = strip_markdown(text)
    else:
        text = normalize_whitespace(text)

    if not text:
        raise ValueError(f"No extractable text found in {path}")

    return ParsedDocument(title=path.stem, source_path=str(path), text=text)


def chunk_text(text: str, max_chars: int = 900, overlap: int = 120) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        cursor = 0
        while cursor < len(paragraph):
            end = min(len(paragraph), cursor + max_chars)
            piece = paragraph[cursor:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(paragraph):
                break
            cursor = max(0, end - overlap)
        current = ""

    if current:
        chunks.append(current)
    return chunks


def best_sentences(question: str, text: str, limit: int = 3) -> list[str]:
    q_tokens = set(tokenize(question))
    ranked: list[tuple[int, str]] = []
    for sentence in re.split(r"(?<=[。！？.!?])\s+|\n+", text):
        cleaned = sentence.strip()
        if len(cleaned) < 18:
            continue
        ranked.append((len(q_tokens.intersection(tokenize(cleaned))), cleaned))
    ranked.sort(key=lambda item: (-item[0], -len(item[1])))
    return [sentence for _, sentence in ranked[:limit]] or [text[:320].strip()]


class KnowledgeBase:
    def __init__(self, root: pathlib.Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"

    def load(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {"documents": [], "chunks": [], "updated_at": now_iso()}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        payload["updated_at"] = now_iso()
        self.index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def ingest_paths(self, paths: Iterable[pathlib.Path]) -> dict[str, int]:
        documents: list[dict[str, Any]] = []
        chunks: list[dict[str, Any]] = []
        doc_count = 0
        chunk_count = 0

        for path in paths:
            parsed = parse_path(path)
            fingerprint = self._fingerprint(path)
            doc_id = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:12]

            documents.append(
                {
                    "id": doc_id,
                    "title": parsed.title,
                    "source_path": parsed.source_path,
                    "fingerprint": fingerprint,
                    "ingested_at": now_iso(),
                }
            )

            for idx, chunk in enumerate(chunk_text(parsed.text), start=1):
                tokens = tokenize(chunk)
                chunks.append(
                    {
                        "id": f"{doc_id}-{idx}",
                        "document_id": doc_id,
                        "title": parsed.title,
                        "source_path": parsed.source_path,
                        "text": chunk,
                        "term_freq": dict(Counter(tokens)),
                    }
                )
                chunk_count += 1

            doc_count += 1

        self.save({"documents": documents, "chunks": chunks})
        return {"documents": doc_count, "chunks": chunk_count}

    def retrieve(self, question: str, top_k: int = 4) -> list[dict[str, Any]]:
        payload = self.load()
        chunks = payload["chunks"]
        q_tokens = tokenize(question)
        if not chunks or not q_tokens:
            return []

        doc_freq: Counter[str] = Counter()
        for token in set(q_tokens):
            for chunk in chunks:
                if token in chunk["term_freq"]:
                    doc_freq[token] += 1

        scored: list[tuple[float, dict[str, Any]]] = []
        total_docs = max(len(chunks), 1)
        for chunk in chunks:
            score = 0.0
            for token in q_tokens:
                freq = chunk["term_freq"].get(token, 0)
                if not freq:
                    continue
                idf = log(1 + (total_docs / (1 + doc_freq[token])))
                score += (1 + log(freq)) * idf
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        preferred_language = detect_question_language(question)
        preferred = [chunk for _, chunk in scored if source_language(chunk["source_path"]) == preferred_language]
        if preferred:
            return preferred[:top_k]
        return [chunk for _, chunk in scored[:top_k]]

    def answer_extractively(self, question: str, top_k: int = 4) -> dict[str, Any]:
        matches = self.retrieve(question, top_k=top_k)
        if not matches:
            language = detect_question_language(question)
            return {
                "answer": (
                    "我没有找到能支撑这个问题的 knockoff 相关证据。"
                    if language == "zh"
                    else "I could not find grounded knockoff-related evidence for that question."
                ),
                "citations": [],
                "matches": [],
                "mode": "empty",
            }

        citations = []
        evidence = []
        for item in matches:
          citations.append(
              {
                  "title": item["title"],
                  "source_path": item["source_path"],
                  "snippet": item["text"][:280].strip(),
              }
          )
          evidence.append(" ".join(best_sentences(question, item["text"])))

        return {
            "answer": " ".join(evidence[:2]).strip(),
            "citations": citations,
            "matches": matches,
            "mode": "extractive",
        }

    @staticmethod
    def _fingerprint(path: pathlib.Path) -> str:
        digest = hashlib.sha1()
        digest.update(str(path.resolve()).encode("utf-8"))
        digest.update(str(path.stat().st_mtime_ns).encode("utf-8"))
        digest.update(str(path.stat().st_size).encode("utf-8"))
        return digest.hexdigest()


def collect_source_files(paths: Iterable[pathlib.Path]) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            files.append(path)
            continue
        if path.is_dir():
            for candidate in path.rglob("*"):
                if candidate.is_file() and candidate.suffix.lower() in TEXT_EXTENSIONS:
                    files.append(candidate)
    return sorted(files)


def display_source_path(path: str) -> str:
    source = pathlib.Path(path)
    try:
        root = pathlib.Path(__file__).resolve().parents[1]
        return str(source.resolve().relative_to(root))
    except Exception:
        return source.name
