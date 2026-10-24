from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import requests

from src.models.base import AnalystPlan


@dataclass
class ModelConfig:
    provider: str = os.getenv("QUERYPILOT_MODEL_PROVIDER", "ollama")
    model: str = os.getenv("QUERYPILOT_MODEL_NAME", "qwen2.5:7b")
    base_url: str = os.getenv("QUERYPILOT_MODEL_URL", "http://localhost:11434")
    timeout: int = int(os.getenv("QUERYPILOT_MODEL_TIMEOUT", "60"))


class ModelUnavailable(RuntimeError):
    pass


class OpenWeightAdapter:
    """Small adapter for Ollama's local HTTP API.

    The adapter only accepts validated JSON. It never receives credentials or executes code.
    """

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()

    def test_connection(self) -> tuple[bool, str]:
        try:
            response = requests.get(f"{self.config.base_url.rstrip('/')}/api/tags", timeout=5)
            response.raise_for_status()
            models = [m.get("name") for m in response.json().get("models", [])]
            if self.config.model not in models:
                return False, f"Ollama is reachable, but model '{self.config.model}' is not installed."
            return True, f"Connected to {self.config.model}"
        except Exception as exc:
            return False, f"Open-weight model unavailable: {str(exc)[:240]}"

    def plan(self, question: str, schema_context: str) -> AnalystPlan:
        prompt = f"""You are QueryPilot AI, a cautious SQL analyst. Return JSON only with keys: intent, relevant_tables, relevant_columns, clarification_needed, sql, assumptions, validation_plan, answer_summary.

Question: {question}

Schema metadata:
{schema_context}

Rules: only produce one read-only SELECT or WITH query; never invent tables or columns; if unsupported set clarification_needed and sql to null; use explicit assumptions."""
        payload = {"model": self.config.model, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0.1}}
        try:
            response = requests.post(f"{self.config.base_url.rstrip('/')}/api/generate", json=payload, timeout=self.config.timeout)
            response.raise_for_status()
            raw = response.json().get("response", "")
            data: Any = json.loads(raw)
            plan = AnalystPlan.model_validate(data)
            if plan.sql and not plan.sql.lstrip().lower().startswith(("select", "with")):
                plan.sql = None
                plan.clarification_needed = "The model returned a non-read-only query, so the request was abstained from."
            return plan
        except Exception as exc:
            raise ModelUnavailable(f"Model inference failed: {str(exc)[:400]}") from exc
