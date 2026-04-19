"""
skill_registry.py — UnifiedSkillRegistry + SkillRouter

Single registry for BOTH command skills (Skill subclasses) and agentic
tools (AgentTool subclasses). Replaces the two disconnected discovery
systems with one queryable, scored, performance-tracking registry.

Scoring algorithm (SkillRouter.score_for_task):
  keyword_overlap  0.00 – 0.40  (word set intersection with tags + description)
  domain_match     0.00 – 0.20  (exact domain match vs. inferred task domain)
  history_bonus    0.00 – 0.20  (skill.success_rate × 0.20)
  cost_penalty    -0.00 – -0.10  (cost_tier × 0.033)
  side_effect_pen -0.00 – -0.15  (0.05 per risky side-effect when task is ambiguous)
  Final score: capped at [0, 1.0]

Performance stats are persisted to data/skill_performance.json using an
exponential moving average (alpha=0.1) so the registry learns over time.
"""

import os
import json
import time
import math
import threading
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Hard-coded metadata for existing skills (avoids decorating every skill class)
# ─────────────────────────────────────────────────────────────────────────────
SKILL_METADATA: Dict[str, Dict] = {
    # ── Command Skills ────────────────────────────────────────────────────────
    "SystemSkill": {
        "domain": "system",
        "tags": ["volume", "brightness", "lock", "battery", "screen", "mute", "unmute", "cpu", "ram", "memory", "sleep"],
        "cost_tier": 0, "requires_network": False, "side_effects": ["modifies_system"],
    },
    "MusicSkill": {
        "domain": "media",
        "tags": ["music", "play", "song", "spotify", "pause", "skip", "next", "previous", "shuffle", "track", "album", "artist", "playlist"],
        "cost_tier": 0, "requires_network": True, "side_effects": ["plays_audio"],
    },
    "CommunicationSkill": {
        "domain": "communication",
        "tags": ["message", "whatsapp", "email", "contact", "send", "text", "call", "imessage"],
        "cost_tier": 0, "requires_network": True, "side_effects": ["sends_message"],
    },
    "WeatherSkill": {
        "domain": "knowledge",
        "tags": ["weather", "temperature", "forecast", "rain", "humidity", "climate"],
        "cost_tier": 1, "requires_network": True, "side_effects": [],
    },
    "NewsSkill": {
        "domain": "knowledge",
        "tags": ["news", "headlines", "latest", "stories", "updates", "breaking"],
        "cost_tier": 1, "requires_network": True, "side_effects": [],
    },
    "CalculatorSkill": {
        "domain": "utility",
        "tags": ["calculate", "math", "compute", "convert", "tip", "percent", "arithmetic"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "SmartThingsSkill": {
        "domain": "iot",
        "tags": ["ac", "air conditioning", "smart", "temperature", "samsung", "thermostat", "switch", "light"],
        "cost_tier": 1, "requires_network": True, "side_effects": ["modifies_system"],
    },
    "ResearchSkill": {
        "domain": "research",
        "tags": ["youtube", "summarize", "analyze", "video", "content", "transcript", "study"],
        "cost_tier": 2, "requires_network": True, "side_effects": [],
    },
    "FileSkill": {
        "domain": "filesystem",
        "tags": ["file", "open", "read", "delete", "folder", "directory", "desktop"],
        "cost_tier": 0, "requires_network": False, "side_effects": ["writes_file"],
    },
    "AppControlSkill": {
        "domain": "system",
        "tags": ["open", "launch", "quit", "close", "app", "application", "safari", "chrome", "vscode"],
        "cost_tier": 0, "requires_network": False, "side_effects": ["modifies_system"],
    },
    "ReminderSkill": {
        "domain": "utility",
        "tags": ["remind", "reminder", "todo", "task", "later", "schedule"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "AlarmSkill": {
        "domain": "utility",
        "tags": ["alarm", "wake", "wake up", "timer", "set alarm"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "TranslatorSkill": {
        "domain": "utility",
        "tags": ["translate", "translation", "french", "spanish", "german", "hindi", "language"],
        "cost_tier": 1, "requires_network": True, "side_effects": [],
    },
    "TimeSkill": {
        "domain": "utility",
        "tags": ["time", "date", "clock", "today", "tomorrow", "what time"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    # ── Agent Tools ───────────────────────────────────────────────────────────
    "web_search": {
        "domain": "research",
        "tags": ["search", "find", "who is", "what is", "news", "google", "web", "internet", "lookup"],
        "cost_tier": 1, "requires_network": True, "side_effects": [],
    },
    "fetch_url": {
        "domain": "research",
        "tags": ["url", "webpage", "fetch", "read", "website", "page", "content"],
        "cost_tier": 1, "requires_network": True, "side_effects": [],
    },
    "get_market_data": {
        "domain": "knowledge",
        "tags": ["price", "rate", "stock", "share", "market", "quote", "gold", "silver", "oil", "crypto", "bitcoin", "ethereum", "currency", "forex", "exchange"],
        "cost_tier": 0, "requires_network": True, "side_effects": [],
    },
    "write_file": {
        "domain": "filesystem",
        "tags": ["file", "write", "save", "create", "output", "export"],
        "cost_tier": 0, "requires_network": False, "side_effects": ["writes_file"],
    },
    "send_message": {
        "domain": "communication",
        "tags": ["whatsapp", "imessage", "message", "send", "contact", "text"],
        "cost_tier": 0, "requires_network": True, "side_effects": ["sends_message"],
    },
    "send_email": {
        "domain": "communication",
        "tags": ["email", "send", "mail", "gmail", "recipient"],
        "cost_tier": 0, "requires_network": True, "side_effects": ["sends_message"],
    },
    "control_music": {
        "domain": "media",
        "tags": ["play", "pause", "skip", "music", "song", "spotify", "resume"],
        "cost_tier": 0, "requires_network": True, "side_effects": ["plays_audio"],
    },
    "control_ac": {
        "domain": "iot",
        "tags": ["ac", "air conditioning", "temperature", "cool", "heat", "fan"],
        "cost_tier": 1, "requires_network": True, "side_effects": ["modifies_system"],
    },
    "get_weather": {
        "domain": "knowledge",
        "tags": ["weather", "temperature", "rain", "forecast", "climate"],
        "cost_tier": 1, "requires_network": True, "side_effects": [],
    },
    "calculator": {
        "domain": "utility",
        "tags": ["calculate", "math", "formula", "expression", "compute"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "manage_reminders": {
        "domain": "utility",
        "tags": ["reminder", "remind", "todo", "task", "add reminder"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "get_system_status": {
        "domain": "system",
        "tags": ["battery", "cpu", "ram", "memory", "uptime", "system info", "status"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "search_awesome_skills": {
        "domain": "meta",
        "tags": ["expert", "skill", "playbook", "specialist", "find expert"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "fetch_skill_playbook": {
        "domain": "meta",
        "tags": ["playbook", "expert", "guideline", "strategy", "best practice"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "remember_fact": {
        "domain": "memory",
        "tags": ["remember", "store", "save", "memorise", "note"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
    "recall_fact": {
        "domain": "memory",
        "tags": ["remember", "recall", "lookup", "what did", "stored"],
        "cost_tier": 0, "requires_network": False, "side_effects": [],
    },
}

# Keywords that signal task domain (for domain_match scoring)
_DOMAIN_SIGNALS: Dict[str, List[str]] = {
    "system":        ["volume", "brightness", "lock screen", "battery", "cpu", "open app", "launch", "quit"],
    "media":         ["play", "music", "song", "spotify", "podcast", "video"],
    "communication": ["send", "message", "email", "whatsapp", "text", "contact"],
    "knowledge":     ["weather", "news", "who is", "what is", "when did", "how many", "current", "price", "rate", "stock", "gold", "currency"],
    "utility":       ["calculate", "remind", "alarm", "translate", "time", "date"],
    "research":      ["research", "summarize", "analyze", "compare", "youtube", "fetch", "find"],
    "filesystem":    ["file", "write", "save", "create file", "desktop", "folder"],
    "iot":           ["ac", "air conditioning", "smart home", "thermostat", "light"],
    "memory":        ["remember", "recall", "store fact", "memorise"],
}


@dataclass
class SkillEntry:
    id: str
    name: str
    skill_type: str          # "command_skill" | "agent_tool"
    description: str
    skill_obj: Any
    domain: str = "general"
    tags: List[str] = field(default_factory=list)
    cost_tier: int = 1
    requires_network: bool = False
    side_effects: List[str] = field(default_factory=list)
    # Performance stats (updated at runtime)
    success_rate: float = 0.85   # Starting prior
    avg_latency_ms: int = 500
    _ema_alpha: float = 0.10     # Exponential moving average factor


class UnifiedSkillRegistry:
    """
    Single registry for all command skills and agent tools.
    Provides task-aware scoring, performance tracking, and persistence.
    """

    _PERF_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "data", "skill_performance.json"
    )

    def __init__(self):
        self._skills: Dict[str, SkillEntry] = {}
        self._lock = threading.RLock()
        self._load_performance_stats()
        logger.info("📚 UnifiedSkillRegistry initialised.")

    # ─────────────────────────────────────────────────────────────────────────
    # Registration
    # ─────────────────────────────────────────────────────────────────────────

    def register_skill(
        self,
        id: str,
        name: str,
        skill_obj: Any,
        skill_type: str = "agent_tool",
        description: str = "",
        domain: str = "general",
        tags: List[str] = None,
        cost_tier: int = 1,
        requires_network: bool = False,
        side_effects: List[str] = None,
    ):
        """Register a skill or agent tool in the unified registry."""
        # Pull from SKILL_METADATA if available (overrides defaults)
        meta = SKILL_METADATA.get(name, SKILL_METADATA.get(id, {}))
        entry = SkillEntry(
            id=id,
            name=name,
            skill_type=skill_type,
            description=description or getattr(skill_obj, "description", name),
            skill_obj=skill_obj,
            domain=meta.get("domain", domain),
            tags=meta.get("tags", tags or []),
            cost_tier=meta.get("cost_tier", cost_tier),
            requires_network=meta.get("requires_network", requires_network),
            side_effects=meta.get("side_effects", side_effects or []),
        )
        with self._lock:
            self._skills[id] = entry
        logger.debug(f"📚 Registered skill: {id} ({skill_type}, domain={entry.domain})")

    # ─────────────────────────────────────────────────────────────────────────
    # Querying
    # ─────────────────────────────────────────────────────────────────────────

    def get_all(self) -> List[SkillEntry]:
        with self._lock:
            return list(self._skills.values())

    def get_by_id(self, skill_id: str) -> Optional[SkillEntry]:
        with self._lock:
            return self._skills.get(skill_id)

    def get_by_domain(self, domain: str) -> List[SkillEntry]:
        with self._lock:
            return [s for s in self._skills.values() if s.domain == domain]

    def get_by_type(self, skill_type: str) -> List[SkillEntry]:
        with self._lock:
            return [s for s in self._skills.values() if s.skill_type == skill_type]

    def get_agent_tools_description(self, top_n: int = 12, task: str = "") -> str:
        """
        Return a formatted description string of the top_n most relevant
        agent tools for a given task. Used by AgentCore to build prompts.
        """
        tools = self.get_by_type("agent_tool")
        if task:
            scored = self._score_entries(task, tools)
            tools = [entry for entry, _ in scored[:top_n]]
        else:
            tools = tools[:top_n]

        lines = [f"- {t.id}: {t.description}" for t in tools]
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # Scoring (SkillRouter logic)
    # ─────────────────────────────────────────────────────────────────────────

    def score_for_task(self, task: str, top_n: int = 12) -> List[Tuple[SkillEntry, float]]:
        """
        Return the top_n skills most relevant to a task, with scores.

        Scoring breakdown:
          keyword_overlap  0.00 – 0.40
          domain_match     0.00 – 0.20
          history_bonus    0.00 – 0.20  (success_rate × 0.20)
          cost_penalty    -0.00 – -0.10  (cost_tier × 0.033)
          side_effect_pen  0.00 – -0.15  (0.05 per risky side-effect)
        """
        with self._lock:
            all_skills = list(self._skills.values())
        scored = self._score_entries(task, all_skills)
        return scored[:top_n]

    def _score_entries(
        self, task: str, entries: List[SkillEntry]
    ) -> List[Tuple[SkillEntry, float]]:
        task_lower = task.lower()
        task_words = set(task_lower.split())
        task_domain = self._infer_task_domain(task_lower)

        results = []
        for entry in entries:
            score = 0.0

            # 1. Keyword overlap (0.0 – 0.40)
            searchable = set(
                " ".join(entry.tags + [entry.description, entry.name]).lower().split()
            )
            overlap = len(task_words & searchable)
            total = max(len(task_words), 1)
            score += min(0.40, (overlap / total) * 0.80)

            # 2. Domain match bonus (0.0 or 0.20)
            if task_domain and entry.domain == task_domain:
                score += 0.20

            # 3. Historical success bonus (0.0 – 0.20)
            score += entry.success_rate * 0.20

            # 4. Cost penalty (-0.10 to 0.0)
            score -= entry.cost_tier * 0.033

            # 5. Side-effect penalty when task is ambiguous
            risky = {"sends_message", "writes_file", "modifies_system", "plays_audio"}
            risky_present = risky & set(entry.side_effects)
            # Only penalise if the task doesn't clearly request a side-effecting action
            action_words = {"send", "write", "open", "play", "turn", "set", "launch"}
            if risky_present and not (action_words & task_words):
                score -= len(risky_present) * 0.05

            results.append((entry, round(max(0.0, min(1.0, score)), 4)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _infer_task_domain(self, task_lower: str) -> Optional[str]:
        """Return the most likely domain for a task string."""
        best_domain = None
        best_count = 0
        for domain, signals in _DOMAIN_SIGNALS.items():
            count = sum(1 for s in signals if s in task_lower)
            if count > best_count:
                best_count = count
                best_domain = domain
        return best_domain if best_count > 0 else None

    # ─────────────────────────────────────────────────────────────────────────
    # Performance Tracking
    # ─────────────────────────────────────────────────────────────────────────

    def record_outcome(self, skill_id: str, success: bool, latency_ms: int):
        """
        Update success_rate and avg_latency_ms with exponential moving average.
        Persists to disk after every update.
        """
        with self._lock:
            entry = self._skills.get(skill_id)
            if not entry:
                return
            alpha = entry._ema_alpha
            entry.success_rate = round(
                alpha * (1.0 if success else 0.0) + (1 - alpha) * entry.success_rate, 4
            )
            entry.avg_latency_ms = int(
                alpha * latency_ms + (1 - alpha) * entry.avg_latency_ms
            )
        self._save_performance_stats()
        logger.debug(
            f"📊 record_outcome: {skill_id} "
            f"success={success} latency={latency_ms}ms "
            f"→ rate={entry.success_rate:.2f}"
        )

    def _load_performance_stats(self):
        """Load persisted performance stats from disk into registry entries."""
        path = os.path.normpath(self._PERF_FILE)
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            with self._lock:
                for skill_id, stats in data.items():
                    if skill_id in self._skills:
                        self._skills[skill_id].success_rate = stats.get("success_rate", 0.85)
                        self._skills[skill_id].avg_latency_ms = stats.get("avg_latency_ms", 500)
            logger.debug(f"📊 Loaded performance stats for {len(data)} skills.")
        except Exception as e:
            logger.warning(f"⚠️ Could not load skill_performance.json: {e}")

    def _save_performance_stats(self):
        """Persist current performance stats to disk."""
        path = os.path.normpath(self._PERF_FILE)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with self._lock:
                data = {
                    sid: {
                        "success_rate": entry.success_rate,
                        "avg_latency_ms": entry.avg_latency_ms,
                    }
                    for sid, entry in self._skills.items()
                }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Could not save skill_performance.json: {e}")
