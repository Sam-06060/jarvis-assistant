import config
import json
import os
import requests
import re
import subprocess
import html
import logging
from datetime import datetime

from modules.web_search import WebSearch

logger = logging.getLogger(__name__)


class AIBrain:
    def __init__(self, context_manager=None, offline_cache=None):
        """Initialize Brain with Cloud-First + Local Fallback"""
        self.context = context_manager
        self.cache = offline_cache
        self.local_model = config.OLLAMA_MODEL
        self.search_engine = WebSearch()
        
        # Cloud-First: Initialize Groq for general conversation
        self.cloud_available = False
        self.groq = None
        if getattr(config, 'CLOUD_FIRST_CONVERSATION', True):
            try:
                from modules.groq_client import GroqClient
                self.groq = GroqClient()
                self.cloud_available = self.groq.available
                if self.cloud_available:
                    self.cloud_model = getattr(config, 'GROQ_CONVERSATION_MODEL', 
                                               getattr(config, 'GROQ_INTENT_MODEL', 'llama-3.3-70b-versatile'))
                    logger.info(f"☁️ Cloud Brain Ready ({self.cloud_model}) — Zero Heat Mode ❄️")
                else:
                    logger.info(f"⚠️ Cloud Brain unavailable — using Local Ollama")
            except Exception as e:
                logger.error(f"⚠️ Cloud Brain init failed: {e} — using Local Ollama")
        
        logger.info(f"🧠 Local Brain Ready ({self.local_model})")

    @property
    def is_online(self):
        """Check if Ollama is reachable"""
        try:
            requests.get(config.OLLAMA_URL, timeout=1)
            return True
        except:
            return False

    def ask(self, text, context=None, web_search=False, system_prompt=None, is_agentic=False):
        """
        Cloud-First Entry Point:
        1. If is_agentic, use the Master Agentic LLM Provider.
        2. Otherwise, use standard Cloud-First logic.
        """
        if is_agentic:
            provider = getattr(config, "AGENTIC_LLM_PROVIDER", "ollama")
            if provider != "ollama":
                # Even if cloud_available was false at init, the Magic Key might have fixed it
                if self.groq:
                    response = self.groq.ask(text, system_prompt=system_prompt, provider=provider)
                    if response:
                        return response
                elif self.cloud_available: # Legacy fallback
                     response = self.groq.ask(text, system_prompt=system_prompt, provider=provider)
                     if response:
                         return response
            # Fallback to local if cloud provider fails or is set to ollama
            return self.ask_local_ollama(text, system_prompt=system_prompt, web_search=web_search)

        if self.cloud_available and getattr(config, 'CLOUD_FIRST_CONVERSATION', True):
            cloud_response = self._ask_cloud(text, web_search=web_search, system_prompt=system_prompt)
            if cloud_response:
                return cloud_response
            logger.warning("☁️ Cloud brain failed — falling back to local Ollama")
        
        return self.ask_local_ollama(text, system_prompt=system_prompt, web_search=web_search)

    def _ask_cloud(self, user_input, web_search=False, system_prompt=None):
        """
        Cloud conversation via Groq (Llama 3.3 70B).
        Zero heat — all computation is remote.
        """
        try:
            # Build persona + context if no custom system prompt provided
            if not system_prompt:
                system_prompt = self._build_system_prompt(user_input, web_search)
            
            # Web search context
            display_query = user_input
            if web_search:
                display_query = self._contextualize_query(user_input)
                logger.info(f"🌍 Searching the web for: '{display_query}'")
                search_context = self.search_engine.search(display_query)
                if search_context:
                    logger.info(f"📝 Injecting Context ({len(search_context)} chars)")
                    system_prompt += self._web_search_prompt(search_context)
            
            final_query = display_query if web_search else user_input
            
            # Call Groq cloud (Hardcoded to Groq for Normal Mode as per user preference)
            print(f"☁️ Asking Cloud Brain ({self.cloud_model})...")
            
            # Use _call_groq directly to ensure normal mode stays on the original path
            response = self.groq._call_groq(
                prompt=final_query,
                system_prompt=system_prompt,
                model=self.cloud_model
            )
            
            if response:
                # Auto-delivery for code blocks (same logic as local)
                has_multiline_code = re.search(r"```[\w]*\n([\s\S]*?)\n```", response)
                if has_multiline_code and len(has_multiline_code.group(1)) > 150:
                    logger.info("📦 Large Code detected. Delivering to Desktop...")
                    return self._deliver_code_to_desktop(response)
                
                logger.debug(f"☁️ Cloud response: {len(response)} chars (zero heat ❄️)")
                return response
            
            return None
            
        except Exception as e:
            logger.warning(f"☁️ Cloud brain error: {e}")
            return None

    def _build_system_prompt(self, user_input, web_search=False):
        """Build the full system prompt with persona + memory"""
        system_prompt = None
        
        # Load Dynamic Persona
        try:
            if hasattr(config, 'PERSONA_FILE') and os.path.exists(config.PERSONA_FILE):
                with open(config.PERSONA_FILE, 'r') as f:
                    system_prompt = f.read().strip()
        except Exception as e:
            logger.error(f"⚠️ Persona Load Error: {e}")

        if not system_prompt:
            system_prompt = "You are Jarvis, a helpful AI assistant. Answer questions directly. If asked for code, generate full, complete code files. Never truncate code."

        # Time context
        current_time = datetime.now().strftime("%A, %B %d, %Y")
        system_prompt = f"Current Date: {current_time}\n" + system_prompt

        # Short-Term Memory
        if self.context and hasattr(self.context, 'get_context_window'):
            memory_block = self.context.get_context_window(limit=5)
            if memory_block:
                system_prompt += f"\n\n{memory_block}"
        
        return system_prompt

    def _web_search_prompt(self, search_context):
        """Build web search injection prompt"""
        return f"""

=== WEB SEARCH RESULTS (ALREADY RETRIEVED FOR YOU) ===
{search_context}

CRITICAL INSTRUCTIONS:
- The web search has ALREADY been performed. The results above are FRESH and CURRENT.
- You MUST answer the user's question using ONLY the search results above.
- NEVER say "I don't have access to real-time data" or "I cannot browse the web" — the data is RIGHT HERE.
- NEVER suggest the user "search the web" — it has ALREADY been done.
- Answer directly and confidently using the provided search results.
- If the results don't contain the answer, say "The search results didn't contain that specific information."
"""

    def ask_local_ollama(self, user_input, system_prompt=None, web_search=False):
        """
        The Robust Local Brain (Llama 3.2).
        Handles queries locally with no rate limits.
        Auto-detects code and delivers it to Desktop.
        """
        
        # --- WEB SEARCH INTEGRATION ---
        search_context = ""
        display_query = user_input  # The query we show/search — may be rewritten with context
        
        if web_search:
            # Step 1: Contextualize the query (resolve pronouns like "he", "she", "his")
            # Ollama is the active brain here, so use Ollama for contextualization
            display_query = self._contextualize_query(user_input, use_cloud=False)
            
            # Step 2: Search the web with the contextualized query
            print(f"🌍 Searching the web for: '{display_query}'")
            search_context = self.search_engine.search(display_query)
            
        if not system_prompt:
            # 1. Load Dynamic Persona
            try:
                if hasattr(config, 'PERSONA_FILE') and os.path.exists(config.PERSONA_FILE):
                    with open(config.PERSONA_FILE, 'r') as f:
                        system_prompt = f.read().strip()
            except Exception as e:
                print(f"⚠️ Persona Load Error: {e}")

            # Fallback if file missing or empty
            if not system_prompt:
                system_prompt = "You are Jarvis, a helpful AI assistant. Answer questions directly. If asked for code, generate full, complete code files. Never truncate code."

        # 0. Global Context Injection (Time/Date)
        current_time = datetime.now().strftime("%A, %B %d, %Y")
        system_prompt = f"Current Date: {current_time}\n" + system_prompt

        # 2. Inject Short-Term Memory
        if self.context and hasattr(self.context, 'get_context_window'):
            memory_block = self.context.get_context_window(limit=5)
            if memory_block:
                print(f"🧠 {memory_block}") # Debug log
                system_prompt += f"\n\n{memory_block}"

        if search_context:
            print(f"📝 Injecting Context ({len(search_context)} chars):\n{search_context[:300]}...")
            # Override the system prompt for web search queries — be extremely firm
            system_prompt += f"""

=== WEB SEARCH RESULTS (ALREADY RETRIEVED FOR YOU) ===
{search_context}

CRITICAL INSTRUCTIONS:
- The web search has ALREADY been performed. The results above are FRESH and CURRENT.
- You MUST answer the user's question using ONLY the search results above.
- The user's question is about the TOPIC in the search results, NOT about you (Jarvis).
- NEVER say "I don't have access to real-time data" or "I cannot browse the web" — the data is RIGHT HERE.
- NEVER suggest the user "search the web" — it has ALREADY been done.
- NEVER talk about yourself or your own history when the user asks about a person or topic.
- Answer directly and confidently using the provided search results.
- If the results don't contain the answer, say "The search results didn't contain that specific information."
"""
        
        # Construct payload — use the contextualized query when web search is active
        final_user_query = display_query if web_search else user_input
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": final_user_query}
        ]
        
        payload = {
            "model": self.local_model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_ctx": 8192,      # Large context window
                "num_predict": -1,    # Infinite generation (no limit)
                "temperature": 0.7
            }
        }

        try:
            # print(f"🧠 Thinking (Local {self.local_model})...") # Reduced log spam
            response = requests.post(f"{config.OLLAMA_URL}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("message", {}).get("content", "")
            
            # === AUTO-DELIVERY LOGIC ===
            # Only trigger if the code block itself is substantial (avoiding markdown text snippets)
            has_multiline_code = re.search(r"```[\w]*\n([\s\S]*?)\n```", answer)
            
            # Threshold: Code block must be > 150 chars to warrant a file download
            if has_multiline_code and len(has_multiline_code.group(1)) > 150:
                print("📦 Large Code detected. Delivering to Desktop...")
                return self._deliver_code_to_desktop(answer)
            
            return answer

        except Exception as e:
            print(f"❌ Local Brain Error: {e}")
            return "I am having trouble thinking locally, sir."

    def _contextualize_query(self, user_input, use_cloud=True):
        """
        Resolves pronouns/ambiguity in short queries using conversation history.
        Example: "How old is he?" -> "How old is Narendra Modi?"

        use_cloud=True  → Groq path (default). Pronoun gate skips API for clear queries.
        use_cloud=False → Ollama path (fallback). Original full logic, Ollama IS running.
        """
        # Skip long queries — already self-contained
        if len(user_input.split()) > 12:
            return user_input

        # Get conversation context (shared by both paths)
        if not self.context or not hasattr(self.context, 'get_context_window'):
            return user_input
        history_text = self.context.get_context_window(limit=2)
        if not history_text:
            return user_input

        # ── GROQ PATH (cloud is up) ─────────────────────────────────────────────
        if use_cloud:
            # Fast gate: only call Groq if pronouns actually need resolving
            pronouns = {"he", "she", "it", "his", "her", "their", "they", "them", "him"}
            has_pronoun = bool(pronouns & set(user_input.lower().split()))
            if not has_pronoun:
                return user_input  # Already clear — zero API cost

            try:
                print("🔄 Contextualizing query via Groq...")
                rewrite_prompt = (
                    f"Rewrite this query to be self-contained by replacing pronouns with actual names from context.\n"
                    f"Output ONLY the rewritten query, nothing else.\n\n"
                    f"Context:\n{history_text}\n\n"
                    f"Query: {user_input}\n"
                    f"Rewritten:"
                )
                refined = self.groq._call_groq(
                    prompt=rewrite_prompt,
                    system_prompt="You are a query rewriter. Output only the rewritten query, no explanation.",
                    model=self.cloud_model
                )
                if refined:
                    refined = refined.strip().strip('"').strip("'")
                    if 2 < len(refined) < 200 and "\n" not in refined:
                        print(f"✅ Contextualized (Groq): '{user_input}' -> '{refined}'")
                        return refined
            except Exception as e:
                print(f"⚠️ Groq contextualization failed: {e}")
            return user_input

        # ── OLLAMA PATH (Groq failed, Ollama is the active brain) ───────────────
        # Original full logic — Ollama IS running here, so we use it directly.
        try:
            print("🔄 Contextualizing query via Ollama...")
            rewrite_prompt = f"""SYSTEM: You are a Query Rewriter. Rewrite the USER QUERY to be self-contained by resolving pronouns and adding context from the RECENT CONVERSATION.

RULES:
1. Replace pronouns (he/she/it/his/her/they/them) with the actual name/topic from context.
2. Keep the original intent and question type intact.
3. Output ONLY the rewritten query. No explanation. No refusal.
4. If the query is already clear (no pronouns or ambiguity), output it unchanged.

EXAMPLES:
- "How old is he?" (Context: Narendra Modi) → "How old is Narendra Modi?"
- "tell his history" (Context: Narendra Modi) → "Tell me about Narendra Modi's history"
- "what work does he do" (Context: Elon Musk) → "What work does Elon Musk do?"
- "is she married" (Context: Taylor Swift) → "Is Taylor Swift married?"
- "who is the president" (no pronoun) → "who is the president"

RECENT CONVERSATION:
{history_text}

USER QUERY: {user_input}

REWRITTEN QUERY:"""

            payload = {
                "model": self.local_model,
                "messages": [{"role": "user", "content": rewrite_prompt}],
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 50}
            }
            response = requests.post(f"{config.OLLAMA_URL}/api/chat", json=payload, timeout=5)
            if response.status_code == 200:
                refined = response.json().get("message", {}).get("content", "").strip()
                if refined and 2 < len(refined) < 200:
                    refined = refined.strip('"').strip("'")
                    print(f"✅ Contextualized (Ollama): '{user_input}' -> '{refined}'")
                    return refined
        except Exception as e:
            print(f"⚠️ Ollama contextualization failed: {e}")

        return user_input


    def _deliver_code_to_desktop(self, text):
        """
        Parses code blocks from text, wraps them in the Interactive HTML Viewer,
        saves to Desktop, and auto-opens it.
        """
        try:
            desktop_path = os.path.expanduser("~/Desktop/Jarvis_Code_Delivery.html")
            
            # Extract Code Blocks
            # Regex to capture: ```(optional_lang)\n(code)```
            code_blocks = re.findall(r"```(\w*)\n(.*?)```", text, re.DOTALL)
            
            if not code_blocks:
                return text # Fallback if regex fails
            
            # Build HTML Content
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis Code Delivery</title>
    <style>
        :root {{ --bg-color: #1e1e1e; --text-color: #d4d4d4; --accent-color: #007acc; --code-bg: #2d2d2d; --header-bg: #252526; }}
        body {{ font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; display: flex; flex-direction: column; gap: 20px; }}
        h1 {{ margin-top: 0; color: #fff; }}
        .file-block {{ background-color: var(--code-bg); border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .file-header {{ background-color: var(--header-bg); padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #3e3e42; }}
        .file-name {{ font-weight: bold; color: #fff; text-transform: uppercase; }}
        .copy-btn {{ background-color: var(--accent-color); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.9em; transition: background 0.2s; }}
        .copy-btn:hover {{ background-color: #005f9e; }}
        .copy-btn:active {{ transform: translateY(1px); }}
        pre {{ margin: 0; padding: 20px; overflow-x: auto; font-family: 'Consolas', monospace; font-size: 14px; line-height: 1.5; color: #dcdcaa; }}
        .success-msg {{ color: #4caf50; margin-left: 10px; font-size: 0.9em; opacity: 0; transition: opacity 0.5s; }}
    </style>
</head>
<body>
    <h1>🚀 Jarvis Delivered Code</h1>
    <p>I have extracted the following code files for you:</p>
"""
            for i, (lang, code) in enumerate(code_blocks):
                lang = lang.strip() if lang else "Code"
                safe_code = html.escape(code)
                block_id = f"code-{i}"
                msg_id = f"msg-{i}"
                
                html_content += f"""
    <div class="file-block">
        <div class="file-header">
            <span class="file-name">{lang}</span>
            <div>
                <span class="success-msg" id="{msg_id}">Copied!</span>
                <button class="copy-btn" onclick="copyCode('{block_id}', '{msg_id}')">Copy Code</button>
            </div>
        </div>
        <pre id="{block_id}">{safe_code}</pre>
    </div>
"""

            html_content += """
    <script>
        function copyCode(elementId, msgId) {
            const code = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(code).then(() => {
                const msg = document.getElementById(msgId);
                msg.style.opacity = 1;
                setTimeout(() => { msg.style.opacity = 0; }, 2000);
            }).catch(err => { console.error('Failed to copy: ', err); alert("Failed to copy code."); });
        }
    </script>
</body>
</html>"""

            # Save File
            with open(desktop_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            # Open File
            subprocess.run(["open", desktop_path])
            
            return "✅ Check your Desktop! I have generated the code and opened it in the viewer for you."

        except Exception as e:
            logger.error(f"⚠️ Code Delivery Failed: {e}")
            return text # Fallback to raw text

    def _handle_code_generation(self, text):
        return text