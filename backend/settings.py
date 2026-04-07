from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass


ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class LLMSettings:
    provider: str = "openai"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-5-mini"
    timeout_seconds: float = 30.0
    requires_api_key: bool = True

    @property
    def configured(self) -> bool:
        if not self.requires_api_key:
            return True
        return bool(self.api_key.strip())


PROVIDER_DEFAULTS = {
    "openai": {
        "api_key_envs": ("OPENAI_API_KEY", "LLM_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-5-mini",
    },
    "groq": {
        "api_key_envs": ("GROQ_API_KEY", "OPENAI_API_KEY", "LLM_API_KEY"),
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
    },
    "openrouter": {
        "api_key_envs": ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "LLM_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openrouter/free",
    },
    "gemini": {
        "api_key_envs": ("GEMINI_API_KEY", "OPENAI_API_KEY", "LLM_API_KEY"),
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash-lite",
    },
    "ollama": {
        "api_key_envs": ("OLLAMA_API_KEY",),
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:3b",
        "requires_api_key": False,
    },
}


def first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def get_llm_settings() -> LLMSettings:
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower() or "openai"
    defaults = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["openai"])

    return LLMSettings(
        provider=provider,
        api_key=first_env(*defaults["api_key_envs"]),
        base_url=os.getenv("OPENAI_BASE_URL", os.getenv("LLM_BASE_URL", defaults["base_url"])),
        model=os.getenv("OPENAI_MODEL", os.getenv("LLM_MODEL", defaults["model"])),
        timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        requires_api_key=bool(defaults.get("requires_api_key", True)),
    )


def knowledge_paths() -> list[pathlib.Path]:
    env_paths = os.getenv("KNOCKOFF_BOT_SOURCES", "").strip()
    if env_paths:
        return [pathlib.Path(part).expanduser() for part in env_paths.split(os.pathsep) if part.strip()]

    return [
        ROOT_DIR / "content",
        ROOT_DIR / "README.md",
    ]
