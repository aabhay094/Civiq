"""
CivicImageAnalyzer — configurable AI vision service.

Reads AI_PROVIDER / AI_API_KEY / AI_MODEL from Django settings (which read
them from environment variables — see settings.py / .env.example).

If no API key is configured, OR the live API call fails for any reason,
this returns a clearly-marked FALLBACK result instead of crashing — the
citizen can still submit their report and edit the category manually.

To add a new provider later: add a `_analyze_with_<provider>()` method and
one line in `analyze()`. Nothing else in the codebase needs to change —
views/services only ever call `CivicImageAnalyzer().analyze(image_bytes)`.
"""

import base64
import json
import logging

import requests
from django.conf import settings

from .prompts import build_analysis_prompt

logger = logging.getLogger(__name__)

ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}


class AIAnalysisError(Exception):
    pass


class CivicImageAnalyzer:
    def __init__(self):
        self.provider = (getattr(settings, "AI_PROVIDER", "") or "").lower()
        self.api_key = getattr(settings, "AI_API_KEY", "")
        self.model = getattr(settings, "AI_MODEL", "")

    def analyze(self, image_bytes, content_type, category_names):
        """
        Returns a dict:
            {
                "problem_type": str,
                "category": str | None,   # must exactly match a category_names entry, or None
                "description": str,
                "priority": "low"|"medium"|"high"|"critical",
                "confidence": float,       # 0.0–1.0
                "is_fallback": bool,       # True if this is NOT a real AI result
            }
        Never raises — always returns a usable dict (falls back on any error).
        """
        if not self.api_key or not self.provider:
            logger.info("AI not configured (no AI_API_KEY/AI_PROVIDER) — using fallback result.")
            return self._fallback_result()

        try:
            if self.provider == "anthropic":
                raw = self._call_anthropic(image_bytes, content_type, category_names)
            else:
                logger.warning("Unknown AI_PROVIDER '%s' — using fallback result.", self.provider)
                return self._fallback_result()

            return self._validate_and_normalize(raw, category_names)
        except Exception:
            logger.exception("AI analysis failed — using fallback result.")
            return self._fallback_result()

    # ------------------------------------------------------------------
    # Provider implementations
    # ------------------------------------------------------------------

    def _call_anthropic(self, image_bytes, content_type, category_names):
        b64_image = base64.b64encode(image_bytes).decode("ascii")
        prompt = build_analysis_prompt(category_names)

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model or "claude-sonnet-4-6",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": content_type,
                                    "data": b64_image,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        text = "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        )
        text = text.strip()
        # Strip accidental markdown fences, just in case
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        return json.loads(text)

    # ------------------------------------------------------------------
    # Validation / fallback
    # ------------------------------------------------------------------

    def _validate_and_normalize(self, raw, category_names):
        if not isinstance(raw, dict):
            raise AIAnalysisError("AI response was not a JSON object.")

        problem_type = str(raw.get("problem_type") or "").strip()[:150]
        description = str(raw.get("description") or "").strip()
        category = raw.get("category")
        priority = str(raw.get("priority") or "medium").strip().lower()
        confidence = raw.get("confidence")

        if category not in category_names:
            category = None  # citizen will pick manually on the review screen

        if priority not in ALLOWED_PRIORITIES:
            priority = "medium"

        try:
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))
        except (TypeError, ValueError):
            confidence = 0.0

        if not description:
            description = "AI could not generate a description for this image — please add one."

        if not problem_type:
            problem_type = "Unclassified Civic Issue"

        return {
            "problem_type": problem_type,
            "category": category,
            "description": description,
            "priority": priority,
            "confidence": confidence,
            "is_fallback": False,
        }

    def _fallback_result(self):
        """
        Honest 'we don't know' result — never pretends to be a real AI
        prediction. The review screen shows a clear notice when is_fallback
        is True, and the citizen picks the category manually.
        """
        return {
            "problem_type": "Unclassified (AI unavailable)",
            "category": None,
            "description": "",
            "priority": "medium",
            "confidence": 0.0,
            "is_fallback": True,
        }
