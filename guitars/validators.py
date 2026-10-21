import re
from django.core.exceptions import ValidationError


def validate_no_spam_links(value):
    """Validate that text does not contain promotional links or URLs."""
    if not value:
        return
    pattern = re.compile(r"https?://|www\.", re.IGNORECASE)
    if pattern.search(value):
        raise ValidationError("Текст не повинен містити інтернет-посилань.")

