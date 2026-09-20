"""
High-level service used by views.py — keeps AI logic out of views entirely.
"""

from civiq.models import Sector

from .analyzer import CivicImageAnalyzer

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


class InvalidImageError(Exception):
    pass


def validate_image_upload(uploaded_file):
    """Raises InvalidImageError with a citizen-friendly message if the
    uploaded file isn't an allowed, reasonably-sized image."""
    content_type = getattr(uploaded_file, "content_type", "") or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidImageError("Please upload a JPEG, PNG, or WEBP image.")
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise InvalidImageError("Image is too large — please use a photo under 8MB.")
    return content_type


def analyze_civic_image(uploaded_file):
    """
    Runs AI analysis on an uploaded image, matched against the CURRENT
    Sector records in the database (so admin-added categories are picked
    up automatically — nothing is hardcoded here).

    Returns a dict (see CivicImageAnalyzer.analyze docstring) plus:
        "sector_id": int | None   (resolved Sector.pk matching "category")
    """
    content_type = validate_image_upload(uploaded_file)

    sectors = list(Sector.objects.all())
    category_names = [s.name for s in sectors]

    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()

    result = CivicImageAnalyzer().analyze(image_bytes, content_type, category_names)

    sector_id = None
    if result["category"]:
        for s in sectors:
            if s.name == result["category"]:
                sector_id = s.id
                break

    result["sector_id"] = sector_id
    return result
