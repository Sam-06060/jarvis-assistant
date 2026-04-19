import os
import re
import json
import config
import logging
from .base import AgentTool

logger = logging.getLogger(__name__)

class SearchAwesomeSkillsTool(AgentTool):
    name = "search_awesome_skills"
    description = "Search the registry of 2200+ expert skills and playbooks. Useful when you need specialized expertise in a domain (e.g. SEO, SaaS, Security). Input: {'query': str}"
    permission = "safe"
    
    def run(self, inp: dict):
        query = inp.get('query', '').strip()
        if not query:
            return "Error: No search query provided."
            
        registry_path = os.path.join(config.ROOT_DIR, "modules", "agent_skills", "_registry.json")
        if not os.path.exists(registry_path):
            return "Error: Skill registry database not found."
            
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            playbooks = data.get("playbooks", {})

            # ── SEMANTIC SEARCH (primary) ──────────────────────────────────────
            try:
                from modules.semantic_router import SemanticRouter
                router = SemanticRouter.instance()
                if router.ready:
                    sem_results = router.search(query, top_k=10)
                    if sem_results:
                        logger.info(f"🧠 [SemanticRouter] Semantic hit for: '{query}' ({len(sem_results)} results)")
                        return self._format_results(
                            [(score, sk_id, playbooks[sk_id]) for sk_id, score in sem_results if sk_id in playbooks],
                            query, source="semantic"
                        )
                else:
                    logger.warning("⚠️ [SemanticRouter] Not ready — falling back to keyword search")
            except Exception as e:
                logger.warning(f"⚠️ [SemanticRouter] Error during search ({e}) — falling back to keyword search")

            # ── KEYWORD SEARCH (fallback) ──────────────────────────────────────
            return self._keyword_search(query, playbooks)

        except Exception as e:
            return f"Failed to search skill registry: {str(e)}"

    def _keyword_search(self, query: str, playbooks: dict) -> str:
        """Original keyword overlap fallback — unchanged logic."""
        query_words = set(query.lower().split())
        results = []
        for skill_id, info in playbooks.items():
            score = 0
            searchable_text = f"{skill_id} {info.get('title', '')} {info.get('summary', '')}".lower()
            for word in query_words:
                if word in searchable_text:
                    score += 1
            if score > 0:
                results.append((score, skill_id, info))

        if not results:
            return f"No expert skills found matching '{query}'. Try broader terms."

        results.sort(key=lambda x: x[0], reverse=True)
        return self._format_results(results[:10], query, source="keyword")

    def _format_results(self, results: list, query: str, source: str = "keyword") -> str:
        """Shared output formatter for both search paths."""
        if not results:
            return f"No expert skills found matching '{query}'. Try broader terms."
        source_tag = "🧠 Semantic" if source == "semantic" else "🔑 Keyword"
        output = [f"{source_tag} search found {len(results)} results for '{query}':"]
        for score, sk_id, info in results:
            output.append(f"\n- **ID: {sk_id}**")
            output.append(f"  Title: {info.get('title', 'N/A')}")
            output.append(f"  Summary: {info.get('summary', '---')}")
            output.append(f"  *Use 'fetch_skill_playbook' with ID '{sk_id}' to read full expertise.*")
        return "\n".join(output)

class FetchSkillPlaybookTool(AgentTool):
    name = "fetch_skill_playbook"
    description = "Retrieve the full expert guidelines and playbooks for a specific skill ID. Use this ONLY after finding a relevant ID via 'search_awesome_skills'. Input: {'skill_id': str}"
    permission = "safe"
    
    def run(self, inp: dict):
        skill_id = inp.get('skill_id', '')
        if not skill_id:
            return "Error: No skill_id provided."
            
        registry_path = os.path.join(config.ROOT_DIR, "modules", "agent_skills", "_registry.json")
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                playbooks = data.get("playbooks", {})
            
            if skill_id not in playbooks:
                return f"Error: Skill ID '{skill_id}' not found in registry."
                
            file_path = playbooks[skill_id].get("path")
            if not file_path or not os.path.exists(file_path):
                return f"Error: Playbook file for '{skill_id}' is missing."
                
            # Header injection with metadata
            meta = playbooks[skill_id]
            header = f"""### [EXPERT SKILL: {meta.get('title', skill_id).upper()}]
- **Risk Level**: {meta.get('risk', 'unknown').upper()}
- **Origin**: OpenClaw Community Registry
- **Context**: This playbook contains hardened guidelines, 'Good/Bad' examples, and Poka-Yoke (Error Proofing) rules.

---
"""
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Strip YAML frontmatter from content to prevent redundant tokens
            content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
                
            # Safety Truncation: 15k chars is usually plenty for expert guidelines
            MAX_REASONABLE_LEN = 15000 
            if len(content) > MAX_REASONABLE_LEN:
                content = content[:MAX_REASONABLE_LEN] + "\n\n... [Content truncated for context safety. Request specific sections if required.]"
            
            # --- AUTO-INJECT INTO ACTIVE CONSTRAINTS ---
            if hasattr(self, 'cp') and hasattr(self.cp, 'memory_vault'):
                # Store the full content into memory vault so the injection loop in agent_core picks it up
                self.cp.memory_vault[f'playbook_{skill_id}'] = f"{header}{content}"
                
            return f"{header}{content}\n\n[SYSTEM NOTE: This playbook has been automatically injected into your active constraints.]"

            
        except Exception as e:
            return f"Failed to fetch playbook: {str(e)}"
