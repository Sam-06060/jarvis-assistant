"""
Cloud API Client for Code Generation.
Primary: OpenRouter (StepFun 3.5 Flash) — User Requested
Fallback: Groq (Qwen3-32B or Llama 70B)
"""

import re
import json
import requests
import logging
import time
import os
import config

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Unified Cloud API Client.
    Supports OpenRouter (Primary) and Groq (Secondary).
    
    SINGLETON: All modules share one instance for connection reuse.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        """Singleton — reuse the same warm connection across all modules."""
        if cls._instance is not None:
            return cls._instance
        cls._instance = super().__new__(cls)
        cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return  # Already initialized — skip
        self._initialized = True
        
        # FORCE RELOAD ENV
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Connection-pooled session (TCP keep-alive, TLS reuse)
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Groq (Fallback + Intent Routing)
        self.groq_api_key = os.getenv("GROQ_API_KEY", config.GROQ_API_KEY)
        self.groq_model = config.GROQ_MODEL
        self.groq_url = config.GROQ_URL
        self.groq_max_tokens = config.GROQ_MAX_TOKENS
        self.groq_available = bool(self.groq_api_key)
        
        # OpenRouter (Primary Code Generation)
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", getattr(config, "OPENROUTER_API_KEY", ""))
        self.openrouter_model = getattr(config, "OPENROUTER_MODEL", "stepfun/step-3.5-flash:free")
        self.openrouter_url = getattr(config, "OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.openrouter_max_tokens = getattr(config, "OPENROUTER_MAX_TOKENS", 32000)
        self.openrouter_available = bool(self.openrouter_api_key)
        
        # Debug Print
        print(f"DEBUG: GroqClient Init - OpenRouter Key Present: {bool(self.openrouter_api_key)}")
        if self.openrouter_api_key:
            print(f"DEBUG: Key starts with: {self.openrouter_api_key[:10]}...")
            
        # Legacy compatibility
        self.api_key = self.groq_api_key
        self.model = self.groq_model
        self.url = self.groq_url
        self.max_tokens = self.groq_max_tokens
        self.available = self.groq_available or self.openrouter_available
        
        if self.openrouter_available:
            logger.info(f"🌐 OpenRouter Ready (Model: {self.openrouter_model})")
        if self.groq_available:
            logger.info(f"☁️ Groq Ready (Model: {self.groq_model}) [Fallback]")
            # Warmup: pre-establish TCP+TLS connection in background
            import threading
            threading.Thread(target=self._warmup_connection, daemon=True).start()
        
        # Track connection health
        self._last_success_time = 0
        self._stale_threshold = 30  # seconds idle before connection considered stale

    def _warmup_connection(self):
        """Pre-establish TCP+TLS connection to Groq."""
        try:
            self.session.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {self.groq_api_key}"},
                timeout=10
            )
            self._last_success_time = time.time()
            logger.info("🔥 Groq connection warmed up")
        except Exception:
            logger.warning("⚠️ Groq warmup failed")

    def _refresh_session(self):
        """Kill dead sockets and create a fresh session."""
        try:
            self.session.close()
        except Exception:
            pass
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        logger.info("🔄 Session refreshed (dead sockets cleared)")

    def _ensure_connection(self):
        """Check if connection is alive. Refresh if stale (e.g., after Jarvis sleep)."""
        elapsed = time.time() - self._last_success_time
        if elapsed < self._stale_threshold:
            return  # Connection used recently — still warm
        
        logger.info(f"🩺 Connection idle {elapsed:.0f}s — health check...")
        try:
            resp = self.session.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {self.groq_api_key}"},
                timeout=5
            )
            if resp.status_code == 200:
                self._last_success_time = time.time()
                logger.info("✅ Connection alive")
                return
        except Exception:
            pass
        
        # Connection is dead — full refresh
        logger.warning("⚠️ Connection stale. Refreshing...")
        self._refresh_session()
        try:
            self.session.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {self.groq_api_key}"},
                timeout=10
            )
            self._last_success_time = time.time()
            logger.info("🔥 Fresh connection established")
        except Exception:
            logger.warning("⚠️ Re-warmup failed — will try real request anyway")

    # ============================================================
    # PUBLIC: Generate code routes
    # ============================================================
    def generate_code(self, prompt, system_prompt=None, model=None):
        """
        Generate code using the best available cloud engine.
        """
        # If a specific model is requested (e.g. IntentRouter wants Llama),
        # always use Groq since that's where Llama lives
        if model and "llama" in model.lower() and not "deepseek" in model.lower():
            return self._call_groq(prompt, system_prompt, model)
        
        # Primary: OpenRouter (StepFun)
        if self.openrouter_available:
            result = self._call_openrouter(prompt, system_prompt)
            if result:
                return result
            logger.warning("⚠️ OpenRouter failed (All retries exhausted). Falling back to Groq.")
        
        # Fallback to Groq
        if self.groq_available:
            return self._call_groq(prompt, system_prompt, model)
            
        return None

    # ============================================================
    # OpenRouter (StepFun 3.5 Flash) - ROBUST CLIENT
    # ============================================================
    def _call_openrouter(self, prompt, system_prompt=None):
        """Call OpenRouter API with streaming for real-time progress updates."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://jarvis-assistant.local",
            "X-Title": "Jarvis Code Architect"
        }
        
        payload = {
            "model": self.openrouter_model,
            "messages": messages,
            "max_tokens": self.openrouter_max_tokens,
            "temperature": 0.3,
            "stream": True  # Enable Streaming
        }
        
        # Enhanced Retry Logic
        max_retries = 5
        backoff_base = 5
        
        # Estimated project size for progress calculation
        ESTIMATED_TOTAL_CHARS = 40000 
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 Sending to OpenRouter ({self.openrouter_model}) [Attempt {attempt+1}/{max_retries}]...")
                
                start_time = time.time()
                response = self.session.post(
                    self.openrouter_url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=30  # Connect timeout (updates keep connection alive)
                )
                
                if response.status_code == 200:
                    full_content = []
                    char_count = 0
                    last_log_time = time.time()
                    
                    # Process Stream
                    for line in response.iter_lines():
                        if not line: continue
                        
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            
                            if data_str == "[DONE]":
                                break
                                
                            try:
                                data_json = json.loads(data_str)
                                choices = data_json.get("choices", [])
                                delta = choices[0].get("delta", {}).get("content", "") if choices else ""
                                
                                if delta:
                                    full_content.append(delta)
                                    char_count += len(delta)
                                    
                                    # Progress Update every 2s or 2000 chars
                                    current_time = time.time()
                                    if current_time - last_log_time > 2.0:
                                        percentage = min(99, int((char_count / ESTIMATED_TOTAL_CHARS) * 100))
                                        logger.info(f"🚀 Generating... {percentage}% ({char_count} chars)")
                                        last_log_time = current_time
                                        
                            except json.JSONDecodeError:
                                continue
                                
                    final_content = "".join(full_content)
                    duration = time.time() - start_time
                    logger.info(f"✅ OpenRouter Complete: {len(final_content)} chars in {duration:.1f}s")
                    
                    # Clean up
                    final_content = re.sub(r'<think>.*?</think>', '', final_content, flags=re.DOTALL).strip()
                    return final_content
                
                elif response.status_code == 429:
                    wait_time = backoff_base * (attempt + 1)
                    logger.warning(f"⚠️ Rate Limited (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code >= 500:
                    logger.warning(f"⚠️ Server Error ({response.status_code}). Retrying...")
                    time.sleep(2)
                    continue
                
                elif response.status_code == 401:
                    logger.error("❌ OpenRouter API key invalid.")
                    return None
                
                else:
                    logger.error(f"❌ OpenRouter error {response.status_code}: {response.text[:300]}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning("⚠️ Connect Timeout. Retrying...")
                time.sleep(2)
                continue
            except requests.exceptions.ConnectionError:
                logger.warning("⚠️ Connection Error. Retrying...")
                time.sleep(5)
                continue
            except Exception as e:
                logger.error(f"❌ Unexpected Error: {e}")
                return None
        
        logger.error("❌ All retries failed for OpenRouter.")
        return None

    # ============================================================
    # Groq (Fallback + Intent Routing) — WITH RETRY
    # ============================================================
    def _call_groq(self, prompt, system_prompt=None, model=None):
        """Call Groq API with connection health management and retry."""
        if not self.groq_available: return None
        
        # PRE-CHECK: ensure connection is alive (catches post-sleep dead sockets)
        self._ensure_connection()
        
        target_model = model if model else self.groq_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": target_model,
            "messages": messages,
            "max_tokens": self.groq_max_tokens,
            "temperature": 0.3
        }
        
        max_retries = 3
        base_timeout = 15  # Start with 15s, doubles each retry
        
        for attempt in range(1, max_retries + 1):
            timeout = base_timeout * attempt  # 15s, 30s, 45s
            try:
                logger.info(f"☁️ Groq ({target_model}) — Attempt {attempt}/{max_retries} (timeout {timeout}s)...")
                response = self.session.post(self.groq_url, headers=headers, json=payload, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    self._last_success_time = time.time()  # Track success
                    logger.info(f"✅ Groq Response: {len(content)} chars (attempt {attempt})")
                    return content
                
                elif response.status_code == 429:
                    # Rate limited — respect Retry-After header if present
                    retry_after = int(response.headers.get("Retry-After", 2 * attempt))
                    logger.warning(f"⚠️ Groq Rate Limited (429). Waiting {retry_after}s before retry...")
                    time.sleep(retry_after)
                    continue
                
                elif response.status_code >= 500:
                    # Server error — retry after backoff
                    wait = 2 * attempt
                    logger.warning(f"⚠️ Groq Server Error ({response.status_code}). Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                
                else:
                    # Client error (401, 400, etc.) — don't retry
                    logger.error(f"❌ Groq Error {response.status_code}: {response.text[:200]}")
                    return None
                    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                error_type = "Timeout" if isinstance(e, requests.exceptions.Timeout) else "Connection Error"
                logger.warning(f"⚠️ Groq {error_type} (attempt {attempt}/{max_retries})")
                
                if attempt < max_retries:
                    # Dead socket — refresh session immediately, NO wait
                    logger.info("🔄 Refreshing session for clean retry...")
                    self._refresh_session()
                continue
                
            except Exception as e:
                logger.error(f"❌ Groq Unexpected Error: {e}")
                return None
        
        logger.error(f"❌ Groq: All {max_retries} attempts failed.")
        return None

