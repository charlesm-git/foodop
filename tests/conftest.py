"""Point the app at a throwaway SQLite file before anything imports the engine.

db.py builds the engine at import time, so this has to run first - conftest is
imported before the test modules, which is exactly the hook we need.
"""

import os
import tempfile

_TMP_DB = os.path.join(tempfile.mkdtemp(prefix="foodop-tests-"), "test.db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP_DB}"
os.environ["OPENAI_API_KEY"] = "test-key-not-real"

from config import get_settings  # noqa: E402

get_settings.cache_clear()
