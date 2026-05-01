import json
import os
import re
from typing import Optional

from google import genai
from google.genai import types

_client: Optional[genai.Client] = None
_resolved_model: Optional[str] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def _resolve_model() -> str:
    global _resolved_model
    if _resolved_model:
        return _resolved_model

    preferred = os.getenv("GEMINI_MODEL")
    if preferred:
        _resolved_model = preferred
        return _resolved_model

    try:
        models = _get_client().models.list()
        for m in models:
            name = getattr(m, "name", "") or ""
            if "flash" in name.lower():
                _resolved_model = name
                return _resolved_model
    except Exception:
        pass

    _resolved_model = "gemini-2.0-flash"
    return _resolved_model


PROMPT_HEADER = """You are a senior software engineer doing a thorough code review.

Analyze the codebase below and respond with ONLY a valid JSON object (no markdown, no commentary) matching this exact shape:

{
  "overall_score": <integer 1-10>,
  "summary": "<2-3 sentence overall assessment>",
  "bugs": [
    {
      "file": "<file path>",
      "line": <integer or null>,
      "severity": "critical" | "warning" | "info",
      "title": "<short title>",
      "description": "<what's wrong and why it matters>",
      "suggested_fix": "<concrete fix>"
    }
  ],
  "quality_issues": [
    {
      "file": "<file path>",
      "severity": "critical" | "warning" | "info",
      "title": "<short title>",
      "description": "<what's wrong and how to improve it>"
    }
  ],
  "suggestions": [
    {
      "file": "<file path>",
      "title": "<short title>",
      "before": "<original code snippet>",
      "after": "<improved code snippet>",
      "explanation": "<why this is better>"
    }
  ]
}

Severity guide:
- critical: bugs/security issues that will break things or expose data
- warning: bug-prone patterns, performance traps, fragile code
- info: style, naming, minor cleanup

Be specific. Reference real file paths and line numbers. Don't invent issues — if the code is solid, return short lists.
"""


def _build_prompt(files: list[dict]) -> str:
    parts = [PROMPT_HEADER, "\n=== CODEBASE ==="]
    for f in files:
        parts.append(f"\n--- FILE: {f['path']} ---\n{f['content']}\n")
    return "\n".join(parts)


def _extract_json(text: str) -> dict:
    # Strip markdown fences if the model added them
    cleaned = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last-ditch: find the first {...} block
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise


def review_code(files: list[dict]) -> dict:
    if not files:
        raise ValueError("No files to review")

    prompt = _build_prompt(files)
    model = _resolve_model()

    response = _get_client().models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )

    raw = response.text or ""
    result = _extract_json(raw)

    result.setdefault("overall_score", 0)
    result.setdefault("summary", "")
    result.setdefault("bugs", [])
    result.setdefault("quality_issues", [])
    result.setdefault("suggestions", [])
    return result
