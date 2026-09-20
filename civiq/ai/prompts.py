"""
Prompt templates for the AI Camera civic-problem analyzer.
Kept separate from analyzer.py so the prompt wording can be tuned without
touching the API-calling logic.
"""


def build_analysis_prompt(category_names):
    """
    category_names: list of existing Sector.name strings from the DB, so the
    AI is asked to match against CIVIQ's real, already-configured categories
    instead of inventing new ones.
    """
    categories_block = "\n".join(f"- {name}" for name in category_names)

    return f"""You are a civic-infrastructure inspector analyzing a citizen-submitted photo for the CIVIQ grievance portal.

Look at the image and identify the civic problem shown (e.g. pothole, garbage dumping, broken streetlight, water leakage, damaged footpath, electrical hazard, etc.).

You MUST choose the "category" field from this exact list of existing CIVIQ categories — copy one of these strings exactly, do not invent a new one:
{categories_block}

If nothing in the list is a good match, set "category" to null.

Respond with ONLY a single JSON object, no other text, no markdown fences, matching exactly this shape:
{{
  "problem_type": "<short 2-4 word label for the specific problem, e.g. 'Pothole'>",
  "category": "<one exact string from the list above, or null>",
  "description": "<one short, factual, civic-official-toned sentence describing only what is visibly evident in the photo — no speculation>",
  "priority": "<one of: low, medium, high, critical>",
  "confidence": <a number between 0.0 and 1.0>
}}

Priority guidance: "critical" only for immediate public-safety hazards (exposed live wires, structural collapse, deep open pits, fire risk). "high" for significant but non-emergency issues (large potholes, major leaks). "medium" for standard issues. "low" for minor/cosmetic issues.

If the image does not show a clear civic infrastructure problem, still return valid JSON with your best-guess fields and a low confidence score — never refuse to return JSON."""
