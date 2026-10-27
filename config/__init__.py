"""Configuration package initialization.

Fixes mysql-connector-python schema editor issue where quote_value fails to
wrap strings in quotes for SQL expressions such as CHECK constraints.
"""

from typing import Any
from mysql.connector.django.schema import DatabaseSchemaEditor


_orig_quote_value = DatabaseSchemaEditor.quote_value


def _patched_quote_value(self, value: Any) -> Any:
    if isinstance(value, str):
        self.connection.ensure_connection()
        escaped = self.connection.connection.converter.escape(value)
        if isinstance(escaped, bytes):
            escaped = escaped.decode()
        escaped = escaped.replace("%", "%%")
        return f"'{escaped}'"
    return _orig_quote_value(self, value)


DatabaseSchemaEditor.quote_value = _patched_quote_value

