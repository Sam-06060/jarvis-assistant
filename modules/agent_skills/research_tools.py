import hashlib
import logging
from .base import AgentTool

logger = logging.getLogger(__name__)

class WebSearchTool(AgentTool):
    name = "web_search"
    description = "Search the internet for information. Input: {'query': str}"
    permission = "safe"

    def run(self, inp: dict):
        query = inp.get('query', '').strip()
        if not query:
            return "Error: 'query' is required."

        # ── Phase 3.2: Within-task search cache ──────────────────────────
        cache_key = f"search_cache_{hashlib.md5(query.lower().encode()).hexdigest()}"
        memory = self.cp.registry.get("memory")
        if memory:
            cached = memory.recall(cache_key)
            if cached:
                logger.info(f"🔍 WebSearch cache HIT for: {query[:60]}")
                return f"[CACHED RESULT]\n{cached}"

        brain = self.cp.registry.get("brain")
        if not brain:
            return "Brain service unavailable."

        result = brain.search_engine.search(query) or "No results found for your query."

        # Store in session cache (TTL: 5 minutes)
        if memory and result and not result.startswith("No results"):
            memory.remember(cache_key, result, ttl_seconds=300)
            logger.info(f"🔍 WebSearch cached result for: {query[:60]}")

        return result


class WebFetchTool(AgentTool):
    name = "fetch_url"
    description = "Fetch full text content from a specific URL. Input: {'url': str}"
    permission = "safe"

    def run(self, inp: dict):
        url = inp.get('url', '').strip()
        if not url:
            return "Error: 'url' is required."

        # ── Cache URL fetches too (same TTL) ─────────────────────────────
        cache_key = f"fetch_cache_{hashlib.md5(url.encode()).hexdigest()}"
        memory = self.cp.registry.get("memory")
        if memory:
            cached = memory.recall(cache_key)
            if cached:
                logger.info(f"🌐 WebFetch cache HIT for: {url[:60]}")
                return f"[CACHED RESULT]\n{cached}"

        brain = self.cp.registry.get("brain")
        if not brain:
            return "Brain service unavailable."

        result = brain.search_engine.fetch_url(url)

        if memory and result:
            memory.remember(cache_key, result, ttl_seconds=300)

        return result



# FileWriteTool has been replaced by SandboxWriteFileTool in sandbox_tools.py
# which enforces sandbox isolation and anti-duplication guards.

