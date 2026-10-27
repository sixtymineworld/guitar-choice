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

# Prevent compound inline foreign key definitions in a single ALTER TABLE
# (ensures compatibility with distributed and cloud MySQL backends like TiDB)
DatabaseSchemaEditor.sql_create_column_inline_fk = None

_orig_skip_default = DatabaseSchemaEditor.skip_default


def _patched_skip_default(self, field: Any) -> bool:
    if getattr(field, "get_internal_type", lambda: "")() == "JSONField":
        return True
    return _orig_skip_default(self, field)


DatabaseSchemaEditor.skip_default = _patched_skip_default



