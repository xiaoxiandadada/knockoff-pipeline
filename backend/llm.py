from __future__ import annotations

from typing import Any

import httpx

from backend.settings import LLMSettings


SYSTEM_PROMPT = """You answer questions using only the supplied knockoff-related evidence.
Rules:
- Answer in exactly the same language as the question.
- Do not mix Chinese and English in the final answer unless the user explicitly asks for bilingual output.
- Prefer evidence written in the same language as the question. If cross-language evidence appears, translate it into the question language before answering.
- Summarize and explain clearly instead of copying large excerpts.
- Use inline citations like [1], [2].
- If the evidence is insufficient, say so plainly.
- Do not invent methods, parameters, or claims.
"""


def generate_answer(question: str, evidence: list[dict[str, Any]], settings: LLMSettings) -> str:
    blocks = []
    for idx, item in enumerate(evidence, start=1):
        blocks.append(
            "\n".join(
                [
                    f"[{idx}] {item['title']}",
                    f"Source: {item['source_path']}",
                    f"Excerpt: {item['text']}",
                ]
            )
        )

    payload = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "\n\n".join(
                    [
                        "Question:",
                        question,
                        "",
                        "Evidence:",
                        "\n\n".join(blocks),
                        "",
                        "Write a concise grounded answer with inline citations in the same language as the question.",
                    ]
                ),
            },
        ],
        "temperature": 0.2,
    }

    headers = {"Content-Type": "application/json"}
    if settings.api_key:
        headers["Authorization"] = f"Bearer {settings.api_key}"

    with httpx.Client(timeout=settings.timeout_seconds) as client:
        response = client.post(f"{settings.base_url.rstrip('/')}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"].strip()
