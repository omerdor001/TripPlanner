import os
import tempfile

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

if not ANTHROPIC_API_KEY:
    raise RuntimeError(
        "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
    )

# Caching of LLM results (the Claude call is slow). Entries are keyed on the
# request parameters plus the prompt/schema, so changing either invalidates them.
CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() not in ("0", "false", "no")
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60)))
# Vercel's filesystem is read-only apart from /tmp, and only lives as long as the
# warm instance — still worth it as a best-effort layer beneath the memory cache.
CACHE_DIR = os.environ.get("CACHE_DIR") or (
    os.path.join(tempfile.gettempdir(), "trip_planner_cache")
    if os.environ.get("VERCEL")
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
)
