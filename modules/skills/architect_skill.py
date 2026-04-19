from .base import Skill
import os
import re
import datetime
import threading
import time
import logging

logger = logging.getLogger(__name__)

class ArchitectSkill(Skill):
    """
    Code Architect — Generates production-ready projects with intelligent stack detection.
    
    Pipeline:
      1. Groq Cloud (Qwen3-32B) → Infers stack & generates code
      2. 5-Stage Context-Aware Verification → Checks if structure matches request
      3. Ollama → Structures into files if XML parsing fails
      4. Saves to ~/Desktop/Jarvis_Builds/
    
    Falls back to local Ollama if Groq is unavailable.
    """
    
    ITERATION_TRIGGERS = [
        "update", "change", "modify", "add", "make", "fix",
        "refactor", "redesign", "overhaul", "improve", "polish"
    ]

    def __init__(self, app):
        super().__init__(app)
        self.last_project_path = None  # GOD MODE: Remember last project for iteration

    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        
        # EXCLUSION GUARD: These are NOT code commands, even if they contain "add"/"make"
        non_code_phrases = [
            "contact", "email", "mail", "call", "message", "text",
            "reminder", "alarm", "timer", "weather", "news",
            "music", "song", "play", "pause", "volume", "brightness",
            "battery", "translate", "calculate", "shortcut",
            "cursor control", "mouse control",
        ]
        if any(phrase in cmd for phrase in non_code_phrases):
            return False
        
        # High-intent triggers (Creation)
        triggers = ["build a", "create a project", "scaffold", "make a app", 
                     "make an app", "write a program", "code a", "build me",
                     "create an app", "make a project", "make me a", "make me an",
                     "design a", "develop a", "generate a"]
        
        if any(t in cmd for t in triggers):
            return True
            
        # Context-aware trigger: If we have a previous project and user says "make it...", handle it
        if self.last_project_path and self._looks_like_project_iteration(cmd):
            return True
        
        # Pattern matching for complex requests
        import re
        if re.search(r'\b(create|build|make|code|write|develop|design|generate)\b.+\b(app|website|site|game|tool|program|project|dashboard|application|system|platform|script|bot|api|server|software|page|component|ui|form|layout|view|screen)\b', cmd):
            return True
            
        return False

    def _looks_like_project_iteration(self, cmd: str) -> bool:
        has_update_verb = any(t in cmd for t in self.ITERATION_TRIGGERS)
        if not has_update_verb:
            return False

        project_reference = re.search(
            r"\b(it|this|that|project|app|application|website|site|ui|layout|screen|page|feature|code|button|chatbox)\b",
            cmd,
        )
        return bool(project_reference)

    def handle(self, command: str) -> bool:
        if "create file" in command.lower(): return False

        self.speech.speak("Architect Protocol Initiated. Determining optimal technology stack...")

        threading.Thread(target=self._run_architect, args=(command,), daemon=True).start()
        return "STOP_LISTENING"  # Auto-sleep while Architect generates in background

    def handle_intent(self, command: str, intent_data: dict) -> bool:
        """
        Direct entry point for NLP Router.
        Bypasses regex checks and uses intent data for context.
        """
        intent = intent_data.get("intent")
        logger.info(f"🧠 Architect triggered via NLP: {intent}")
        
        self.speech.speak("Architect Protocol Initiated via Neural Link...")
        threading.Thread(target=self._run_architect, args=(command, intent), daemon=True).start()
        return "STOP_LISTENING"  # Auto-sleep while Architect generates in background

    # ============================================================
    # V2 ITERATIVE PIPELINE (Architect V2)
    # ============================================================
    def _run_v2_pipeline(self, command, system_prompt, is_iteration, groq_instance):
        """
        The Iterative Beast — Generates large projects in 20K token slots.
        """
        self.brain = self.app.get('brain')
        provider = groq_instance if groq_instance.available else self.brain
        
        # Phase 1: Blueprint
        self.speech.speak("Designing V2 project blueprint...")
        blueprint = self._generate_v2_blueprint(command, system_prompt, provider)
        if not blueprint:
             self.speech.speak("Blueprint generation failed. Falling back to legacy pass.")
             return False # Signal fallback

        # Phase 2: Iterative Slot Generation
        project_files = []
        remaining_files = blueprint.copy()
        generated_meta = []
        
        iteration = 1
        while remaining_files:
            logger.info(f"🚀 V2 Iteration {iteration}: {len(remaining_files)} files remaining.")
            self.speech.speak(f"Construction phase {iteration} initiated...")

            # Select batch for 20K token slot
            # Reduced to 1-2 files for maximum reliability/budget per file
            batch_size = 2 if len(remaining_files) > 5 else 1
            batch = remaining_files[:batch_size]
            remaining_files = remaining_files[batch_size:]

            slot_code = self._generate_v2_slot(command, system_prompt, batch, generated_meta, provider)
            if not slot_code:
                logger.warning(f"⚠️ Slot failed in iteration {iteration}. Retrying...")
                remaining_files = batch + remaining_files
                continue

            # Parse & Safe-Cut Guard
            slot_matches = self._parse_v2_slot(slot_code, batch)
            
            if slot_matches:
                # INCREMENTAL SAVING: Write these files to the desktop IMMEDIATELY
                logger.info(f"📂 V2 Incremental Save: Writing {len(slot_matches)} files...")
                # We use is_iteration=True for subsequent slots to keep writing to the same folder
                current_is_iteration = is_iteration if iteration == 1 else True
                self._incremental_build_v2(slot_matches, command, current_is_iteration)
                
                for fname, content in slot_matches:
                    project_files.append((fname, content))
                    generated_meta.append(f"{fname} ({len(content)} bytes)")
                    logger.info(f"   ✅ V2 Structured: {fname}")

            iteration += 1
            if iteration > 15: 
                logger.warning("🏁 Global safety break triggered (limit 15 iterations).")
                break 

        # Phase 3: Final Verification
        self.speech.speak("Performing final project integrity check...")
        logger.info("🔍 V2 Final Verification Phase...")
        missing_files = []
        for f in blueprint:
            if not any(pf[0] == f['file'] for pf in project_files):
                missing_files.append(f['file'])
        
        if missing_files:
            logger.warning(f"⚠️ Missing files detected: {missing_files}. Triggering recovery...")
            self.speech.speak("I noticed some missing components. Recovering now...")
            # Brief recovery call for missing files
            recovery_batch = [{"file": f, "purpose": "Recovering missing file"} for f in missing_files]
            recovery_code = self._generate_v2_slot(command, system_prompt, recovery_batch, generated_meta, provider)
            recovery_matches = self._parse_v2_slot(recovery_code, recovery_batch)
            if recovery_matches:
                self._incremental_build_v2(recovery_matches, command, True)
                logger.info(f"✅ Recovery successful for {len(recovery_matches)} files.")

        self.speech.speak("Project construction and verification complete.")
        return True

    def _generate_v2_blueprint(self, command, system_prompt, provider):
        """Map out the entire project structure first."""
        logger.info("🗺️  Generating Blueprint...")
        prompt = f"""
USER REQUEST: {command}

You are a Lead Architect. Define the full production-ready file structure for this request.
Include every component, route, and config file needed.

OUTPUT FORMAT (JSON ONLY):
[
  {{"file": "filename.ext", "purpose": "description"}},
  ...
]
"""
        response = provider.generate_code(prompt=prompt, system_prompt=system_prompt) if hasattr(provider, 'generate_code') else provider.ask(prompt, system_prompt=system_prompt)
        
        if not response:
            logger.error("❌ Blueprint Response Empty.")
            return None

        blueprint = self._extract_json_array(response)
        if blueprint:
            logger.info(f"✅ Blueprint mapped: {len(blueprint)} files identified.")
            return blueprint
        else:
            logger.error(f"❌ Blueprint JSON Parse Error. Raw Output:\n{response}")
            return None

    def _extract_json_array(self, text):
        """
        Extremely robust JSON array extractor with Auto-Repair.
        Handles markdown backticks, conversational filler, and truncation.
        """
        import json
        if not text: return None
        text = text.strip()
        
        # 0. Strip possible markdown code block wrappers
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        
        # 1. Try direct find for any array [ ] structure
        start = text.find('[')
        end = text.rfind(']')
        
        if start != -1 and end != -1:
            json_str = text[start:end+1]
        if start != -1:
            # Try to find the best possible ending
            potential_ends = [i for i, char in enumerate(text) if char == '}']
            for p_end in reversed(potential_ends):
                # Try closing the array here
                candidate = text[start:p_end+1] + "]"
                try:
                    return json.loads(candidate)
                except:
                    continue
            
            # If no array closure worked, try the raw text if it was already closed
            if end != -1:
                try: return json.loads(text[start:end+1])
                except: pass
        
        # 3. Last ditch: Regex find logic
        matches = re.findall(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if matches:
            for m in reversed(matches): # Try largest/last matches first
                try: return json.loads(m)
                except: pass
            
        return None

    def _generate_v2_slot(self, command, system_prompt, batch, generated_meta, provider):
        """Generate a cluster of files."""
        file_list = "\n".join([f"- {f['file']}: {f['purpose']}" for f in batch])
        context = "\n".join(generated_meta)
        
        prompt = f"""
PROJECT: {command}
ALREADY GENERATED:
{context if context else "(None)"}

YOUR TASK: Write COMPLETE code for these files:
{file_list}

V2 RULES:
1. OUTPUT RAW XML ONLY: <file name="filename">...</file>
2. 20K SLOT: If you hit token limits, stop only AFTER a complete file.
3. NO STUBS: Full production code only.
"""
        return provider.generate_code(prompt=prompt, system_prompt=system_prompt) if hasattr(provider, 'generate_code') else provider.ask(prompt, system_prompt=system_prompt)

    def _parse_v2_slot(self, response, batch):
        """Extract files with Safe-Cut protection."""
        matches = re.findall(r'<file name="(.*?)">(.*?)</file>', response, re.DOTALL)
        
        if not matches:
             logger.error(f"❌ V2 Slot Parsing Failed. Expected files: {[f['file'] for f in batch]}. Raw Response:\n{response}")
             return []

        valid = []
        for name, content in matches:
            if content.strip().endswith('...'):
                logger.warning(f"⚠️ Safe-Cut: {name} incomplete. Deferring to next slot.")
                continue
            valid.append((name.strip(), content.strip()))
        return valid

    def _incremental_build_v2(self, project_files, command, is_iteration):
        """Bridge to existing build logic for incremental writes."""
        self._build_project_actual(None, command, is_iteration=is_iteration, matches=project_files)

    def _run_architect(self, command, intent=None):
        brain = self.app.get('brain')
        if not brain:
            self.speech.speak("Brain module unavailable.")
            return

        # ============== GOD MODE: CONTEXT LOADING ==============
        previous_context = ""
        is_iteration = False # Default checks
        
        # 1. AUTO-RECOVERY
        if not self.last_project_path:
            builds_dir = os.path.expanduser("~/Desktop/Jarvis_Builds")
            if os.path.exists(builds_dir):
                dirs = [os.path.join(builds_dir, d) for d in os.listdir(builds_dir) if os.path.isdir(os.path.join(builds_dir, d))]
                if dirs:
                    last_built = max(dirs, key=os.path.getmtime)
                    if os.listdir(last_built):
                        self.last_project_path = last_built
                        logger.info(f"🔄 Restored context from latest build: {self.last_project_path}")

        # 2. DETERMINE MODE (NEW vs MINOR vs MAJOR)
        mode = "NEW"
        
        if intent == "ARCHITECT_UPDATE_MINOR":
            mode = "MINOR"
        elif intent == "ARCHITECT_UPDATE_MAJOR":
            mode = "MAJOR"
        elif intent == "ARCHITECT_NEW":
            mode = "NEW"
            # PHASE 8.3: Clean slate for new projects
            # Prevents auto-recovery from polluting the next build
            self.last_project_path = None
            logger.info("🧹 Context cleared for new project.")
            
        logger.info(f"🏗️ Architect Mode: {mode}")

        # 3. LOAD CONTEXT (If Update)
        if mode in ["MINOR", "MAJOR"] and self.last_project_path:
            logger.info(f"🔄 Iteration/Overhaul detected on: {self.last_project_path}")
            previous_context = self._load_project_context(self.last_project_path)
            if previous_context:
                is_iteration = True
                self.speech.speak("Loading previous project context...")


        if mode == "MINOR":
            # DIGITAL SURGEON MODE (Precise Tweaks)
            system_prompt = """
You are a Senior Code Refactorer & Digital Surgeon.
Your goal is to MAKE PRECISE EDITS to the existing codebase based on the user request.

CRITICAL RULES:
1. **NO REWRITES**: Do NOT rewrite the entire application. Only modify the specific files requested.
2. **PRESERVE LOGIC**: Keep all existing logic and styles unless explicitly asked to change them.
3. **PRESERVE MANUAL EDITS**:
   - The user may have manually added code (e.g. smooth scrolling, analytics).
   - SCAN the `PREVIOUS PROJECT CONTEXT` carefully.
   - If you see custom functions or scripts, **KEEP THEM**.
   - Do NOT simplify the code just because you can.
4. **FILE FORMAT**:
   <file name="filename">
   ... full content ...
   </file>
5. **OUTPUT**:
   - Return the FULL CONTENT of the modified file.
   - Do NOT return unaffected files.
   - Do NOT use diffs (like `// ... existing code ...`). Return the COMPLETE valid file.
"""
        else:
            # CREATIVE ARCHITECT MODE (New Build OR Major Redesign)
            # Used for "NEW" and "MAJOR" (Recreate)
            system_prompt = """
3. **FLUID & SCALABLE DESIGN (Crucial)**:
   - **NO FIXED WIDTHS**: Never use `width: 400px` for main containers. Use `width: min(90%, 1400px)` or `max-width`.
   - **FLUID TYPOGRAPHY**: Use `clamp(2rem, 5vw, 5rem)` for headings. Use `rem` for body text.
   - **SCALABLE GRIDS**: Use `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`.
   - **FULL HEIGHT**: Use `min-height: 100vh` for hero sections.
   - **UNITS**: Use `%`, `vw`, `vh`, `fr`, `rem`. Avoid `px` for layout.

4. **SELF-CONTAINED**:
   - Use CDNs for libraries (Tailwind, GSAP, Three.js, FontAwesome).
   - No placeholders. Full working code.

5. **FORMAT**:
<file name="filename">
content
</file>

Failure to separate files or producing "basic/fixed" code is UNACCEPTABLE.
"""

        # ============== STAGE 1: V2 PIPELINE (ITERATIVE) ==============
        # We always use V2 for Major/New requests to handle scale.
        try:
            from modules.groq_client import GroqClient
            groq = GroqClient()
            
            # Initiate V2 Pipeline
            success = self._run_v2_pipeline(command, system_prompt, is_iteration, groq)
            
            if not success:
                 # Legacy Fallback logic if V2 fails
                 self.speech.speak("V2 blueprint failed. Using legacy single-pass...")
                 current_code = brain.ask_local_ollama(
                     command + " (OUTPUT RAW XML ONLY)", 
                     system_prompt=system_prompt
                 )
                 self._build_project_actual(current_code, command, is_iteration=is_iteration)

        except Exception as e:
            logger.error(f"❌ V2 Pipeline Error: {e}")
            self.speech.speak("Architect V2 encountered an error. Falling back.")
            # Final safety fallback
            current_code = brain.ask_local_ollama(command, system_prompt=system_prompt)
            self._build_project_actual(current_code, command, is_iteration=is_iteration)

    # ============================================================
    # MULTI-PASS GENERATION (Legacy Stage 9)
    # ============================================================
    def _count_stubs(self, code: str) -> int:
        """Count how many <file> blocks contain stubs (... or very short content)."""
        import re
        files = re.findall(r'<file\s+name="([^"]+)">\s*(.*?)\s*</file>', code, re.DOTALL)
        stub_count = 0
        for name, content in files:
            content = content.strip()
            if content in ['...', '…', ''] or len(content) < 20:
                stub_count += 1
        return stub_count

    def _multi_pass_generate(self, command: str, system_prompt: str, groq, initial_code: str) -> str:
        """
        Multi-Pass Architecture (Stage 9).
        When the initial generation returns stubs, generate each file individually.
        
        Strategy:
        1. Parse file names + descriptions from initial output
        2. Generate each file in a separate API call (full token budget per file)
        3. Combine into final XML output
        """
        import re
        
        # Extract file plan from initial (stub) output
        files = re.findall(r'<file\s+name="([^"]+)">\s*(.*?)\s*</file>', initial_code, re.DOTALL)
        
        if not files:
            logger.warning("⚠️ Multi-pass: No files found in initial output. Using single-pass result.")
            return initial_code
        
        logger.info(f"🔄 Multi-Pass Mode: {len(files)} files to generate individually")
        
        # Build file list for context
        file_list = "\n".join([f"  - {name}" for name, _ in files])
        
        all_code_parts = []
        generated_so_far = []  # Track what we've generated for inter-file context
        
        for i, (filename, existing_content) in enumerate(files):
            existing_content = existing_content.strip()
            is_stub = existing_content in ['...', '…', ''] or len(existing_content) < 20
            
            if not is_stub and len(existing_content) > 50:
                # This file already has real content, keep it
                all_code_parts.append(f'<file name="{filename}">\n{existing_content}\n</file>')
                generated_so_far.append(f"  - {filename} (already generated)")
                logger.info(f"   ✅ Kept existing: {filename} ({len(existing_content)} chars)")
                continue
            
            # Generate this file individually
            logger.info(f"   🔨 Generating [{i+1}/{len(files)}]: {filename}")
            self.speech.speak(f"Writing {filename}...")
            
            # Build context-aware prompt for this specific file
            file_prompt = f"""
PROJECT: {command}

ALL FILES IN THIS PROJECT:
{file_list}

FILES ALREADY GENERATED:
{chr(10).join(generated_so_far) if generated_so_far else "  (none yet — this is the first file)"}

YOUR TASK: Write the COMPLETE code for this ONE file:
  FILE: {filename}

RULES:
1. Output ONLY the raw code for {filename}. No markdown, no explanations, no XML tags.
2. Write PRODUCTION-QUALITY code. No placeholders, no "TODO", no "...".
3. The code must work with the other files in this project.
4. Write the FULL, COMPLETE implementation.
"""
            
            file_code = groq.generate_code(prompt=file_prompt, system_prompt=system_prompt)
            
            if file_code:
                # Clean up — remove any accidental XML/markdown wrapping
                file_code = re.sub(r'^```\w*\s*', '', file_code)
                file_code = re.sub(r'\s*```$', '', file_code)
                file_code = re.sub(r'^<file[^>]*>', '', file_code)
                file_code = re.sub(r'</file>$', '', file_code)
                file_code = file_code.strip()
                
                all_code_parts.append(f'<file name="{filename}">\n{file_code}\n</file>')
                generated_so_far.append(f"  - {filename} ({len(file_code)} chars)")
                logger.info(f"   ✅ Generated: {filename} ({len(file_code)} chars)")
            else:
                logger.error(f"   ❌ Failed to generate: {filename}")
                all_code_parts.append(f'<file name="{filename}">\n// Generation failed for {filename}\n</file>')
                generated_so_far.append(f"  - {filename} (FAILED)")
        
        return "\n\n".join(all_code_parts)

    def _load_project_context(self, path):
        """GOD MODE: Read all files in the project path."""
        try:
            context = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.startswith(".") or "__pycache__" in root: continue
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, path)
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        context.append(f'<file name="{rel_path}">\n{content}\n</file>')
            return "\n".join(context)
        except Exception as e:
            logger.error(f"⚠️ Failed to load previous context: {e}")
            return ""

    def _get_next_version_name(self, directory, filename):
        """
        Generates the next version filename (e.g., style.css -> style_v2.css).
        """
        name, ext = os.path.splitext(filename)
        # Strip existing version if present (just in case)
        name = re.sub(r'_v\d+$', '', name)
        
        max_v = 1
        # Check if base file exists (e.g. style.css)
        if os.path.exists(os.path.join(directory, filename)):
            max_v = 1
            
        # Scan for existing versions
        for f in os.listdir(directory):
            if f.startswith(name) and f.endswith(ext):
                match = re.search(rf'{re.escape(name)}_v(\d+){re.escape(ext)}$', f)
                if match:
                    v = int(match.group(1))
                    if v > max_v: max_v = v
        
        # If no base file and no versions, return original
        if max_v == 1 and not os.path.exists(os.path.join(directory, filename)):
            return filename
            
        return f"{name}_v{max_v + 1}{ext}"

    def _build_project_actual(self, llm_response, original_command, source="unknown", is_iteration=False, matches=None):
        """
        Final construction phase. 
        Accepts:
          - llm_response: Raw XML string (Legacy)
          - matches: Pre-parsed (name, content) list (V2)
        """
        import shutil
        from datetime import datetime # Added for datetime.now()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. SETUP PATHS
        if is_iteration and self.last_project_path and os.path.exists(self.last_project_path):
             base_name = os.path.basename(self.last_project_path)
             match = re.search(r'_v(\d+)$', base_name)
             if match:
                 v = int(match.group(1))
                 new_name = re.sub(r'_v\d+$', f'_v{v+1}', base_name)
             else:
                 new_name = f"{base_name}_v2"
             
             parent_dir = os.path.dirname(self.last_project_path)
             base_path = os.path.join(parent_dir, new_name)
             
             logger.info(f"🔄 V2 Snapshot: {base_path}")
             try:
                 shutil.copytree(self.last_project_path, base_path)
             except Exception as e:
                 logger.error(f"⚠️ Snapshot copy failed: {e}") # Added missing print for error
                 os.makedirs(base_path, exist_ok=True)
             project_name = new_name
             
        else:
             project_name = self._generate_project_name(original_command)
             builds_dir = os.path.expanduser("~/Desktop/Jarvis_Builds")
             base_path = os.path.join(builds_dir, f"{project_name}_{timestamp}")
             os.makedirs(base_path, exist_ok=True)
             logger.info(f"📂 V2 Project Folder: {base_path}")

        # 2. EXTRACT FILES (If not already provided via V2)
        if not matches:
            pattern = r'<file name="(.*?)">(.*?)</file>'
            matches = re.findall(pattern, llm_response, re.DOTALL)
            
            if not matches:
                logger.warning("⚠️ XML parsing failed. Attempting repair with Ollama...")
                matches = self._repair_with_ollama(llm_response)
            
            if not matches:
                self.speech.speak("Code was generated, but I couldn't parse the file structure. Check the logs.")
                logger.error(f"❌ Architect Failure. Source: {source}. Raw output:\n{llm_response[:1000]}")
                return

        # 3. VERIFY & WRITE
        matches = self._ensure_critical_files(matches, original_command)

        # Create Directory & Write Files
        try:
            file_count = 0
            for filename, content in matches:
                filename = filename.strip()
                content = content.strip()
                
                # Security: Prevent escaping directory
                if ".." in filename or filename.startswith("/"):
                    continue
                
                # STAGE 4: OVERWRITE in new folder (No more file versioning like style_v2.css)
                full_path = os.path.join(base_path, filename)
                
                # Ensure subfolders exist
                file_dir = os.path.dirname(full_path)
                if file_dir:
                    os.makedirs(file_dir, exist_ok=True)
                
                # Phase 3.2 & 6.2: Integrity Assurance (Snippet Blocking)
                if is_iteration and os.path.exists(full_path):
                     try:
                         with open(full_path, "r", encoding="utf-8") as f_old:
                             old_content = f_old.read()
                             
                         # 6.1: Idempotency Check
                         if old_content.strip() == content.strip():
                             print(f"   ⏭️ Skipped (Identical): {filename}")
                             continue

                         old_size = len(old_content)
                         new_size = len(content)
                         
                         # 6.2: Strict Snippet Guard
                         # If new content is < 50% of old, assume it's a snippet/error and REJECT IT.
                         # Exception: If user explicitly asked to "remove" or "delete"? 
                         # (For now, prioritize safety. User ca delete manually).
                         if old_size > 300 and new_size < old_size * 0.5:
                             print(f"⚠️ SNIPPET BLOCKED in {filename} ({old_size} -> {new_size} bytes). Update Rejected.")
                             self.speech.speak(f"I blocked a partial update to {filename} to prevent code loss.")
                             # Save the snippet as a .snippet file for review, but DO NOT OVERWRITE
                             with open(full_path + ".snippet", "w", encoding="utf-8") as f_snippet:
                                 f_snippet.write(content)
                             continue
                             
                     except Exception as e:
                         logger.error(f"⚠️ Integrity check error: {e}")

                # Verify directory exists (again, safety)
                if file_dir and not os.path.exists(file_dir):
                    os.makedirs(file_dir)

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                logger.info(f"   📄 Wrote: {os.path.basename(full_path)}")
                file_count += 1
            
            # GOD MODE: Save path for next iteration
            self.last_project_path = base_path
            
            # Report success
            if is_iteration:
                success_msg = f"Update complete. Created snapshot {project_name}."
            else:
                success_msg = f"Project built. {file_count} files created in {project_name}."
                
            # Phase 1.2: Update Manifest
            file_list = [m[0] for m in matches]
            self._update_project_manifest(base_path, original_command, file_list)
                
            self.speech.speak(success_msg)
            logger.info(f"✅ {success_msg}")
            
            # Open the folder in Finder
            import subprocess
            subprocess.run(["open", base_path])
            
            # Phase 3.3: Auto-Preview (Web) - DISABLED per user request
            # if os.path.exists(os.path.join(base_path, "index.html")):
            #      subprocess.run(["open", os.path.join(base_path, "index.html")])
            #      print("🌍 Launched Browser Preview")
            
        except Exception as e:
            self.speech.speak("Construction failed due to a system error.")
            logger.error(f"❌ Architect Error: {e}")

    def _generate_project_name(self, command):
        # Noise: words that don't help project names
        noise_words = {
            "build", "create", "scaffold", "make", "write", "code", "generate",
            "a", "an", "the", "me", "for", "please", "can", "you", "project",
            "program", "app", "application", "software", "tool", "using",
            "are", "senior", "full-stack", "engineer", "and", "product"
        }
        
        # Clean the string from punctuation and split
        clean_text = re.sub(r'[^\w\s]', ' ', command)
        words = clean_text.lower().split()
        
        relevant = [w for w in words if w not in noise_words and len(w) > 1]
        
        if not relevant:
            helpful_context = [w for w in words if len(w) > 2][:3]
            relevant = helpful_context or ["Jarvis_Project"]
        
        # Capitalize and join with underscore (Limit to top bits of meaning)
        return "_".join(w.capitalize() for w in relevant[:4])

    def _repair_with_ollama(self, raw_response):
        """
        Use local Ollama to reformat broken XML output.
        This is Stage 3B — only called if XML parsing fails.
        """
        brain = self.app.get('brain')
        if not brain:
            return []
        
        try:
            repair_prompt = f"""I have code output that needs to be wrapped in XML file tags.
Convert this into proper XML format with <file name="filename">content</file> tags.
Output ONLY the XML tags, nothing else.

RAW CODE:
{raw_response[:6000]}"""

            repair_response = brain.ask_local_ollama(repair_prompt)
            
            if repair_response:
                pattern = r'<file name="(.*?)">(.*?)</file>'
                matches = re.findall(pattern, repair_response, re.DOTALL)
                if matches:
                    logger.info(f"✅ Ollama repair successful: {len(matches)} files extracted")
                    return matches
        except Exception as e:
            logger.error(f"⚠️ Ollama repair failed: {e}")
        
        return []

    def _update_project_manifest(self, project_path, command, file_list):
        """Phase 1.2: Maintain a 'jarvis_manifest.json'."""
        import json
        manifest_path = os.path.join(project_path, "jarvis_manifest.json")
        
        stack = "unknown"
        if any(f.endswith(".html") for f in file_list): stack = "web_vanilla"
        if any(f.endswith("package.json") for f in file_list): stack = "node_js"
        if any(f.endswith(".py") for f in file_list): stack = "python"
        
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command,
            "files_modified": file_list
        }
        
        data = {
            "project_name": os.path.basename(project_path),
            "stack": stack,
            "created_at": entry["timestamp"],
            "version": 1,
            "history": [entry]
        }
        
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    old_data = json.load(f)
                    data = old_data
                    data["version"] = data.get("version", 1) + 1
                    data["stack"] = stack 
                    if "history" not in data: data["history"] = []
                    data["history"].append(entry)
            except: pass
                
        with open(manifest_path, 'w') as f:
            json.dump(data, f, indent=2)
            logger.info(f"🧠 Project Manifest updated (v{data['version']})")

    def _enhance_assets(self, content, file_ext):
        """
        Phase 2.2: Intelligent Asset Replacement.
        Scans for <img> tags and replaces empty/placeholder src with Unsplash.
        """
        if file_ext not in [".html", ".jsx", ".tsx", ".vue"]:
            return content
            
        # Regex to find <img> tags with empty or generic src
        # e.g. <img src="" or <img src="placeholder.jpg"
        # We replace with source.unsplash.com/random/800x600/?{keyword}
        
        def replace_match(match):
            full_tag = match.group(0)
            if "unsplash" in full_tag: return full_tag # Already good
            
            # Simple keyword extraction from alt text or just random context
            keyword = "technology" 
            if 'alt="' in full_tag:
                # Try to grab alt word
                try:
                    alt = re.search(r'alt="(.*?)"', full_tag).group(1)
                    if alt: keyword = alt.split()[0]
                except: pass
            
            new_src = f"https://source.unsplash.com/random/800x600/?{keyword}"
            # Replace the src attribute match
            return re.sub(r'src=".*?"', f'src="{new_src}"', full_tag)

        # Find img tags
        # content = re.sub(r'<img[^>]+src=["\'](.*?)["\'][^>]*>', replace_match, content)
        # Actually simpler to just replace explicit bad srcs
        
        # 1. Replace empty src
        content = content.replace('src=""', 'src="https://source.unsplash.com/random/800x600/?abstract"')
        content = content.replace("src=''", "src='https://source.unsplash.com/random/800x600/?abstract'")
        
        # 2. Replace "placeholder"
        if "placeholder" in content:
            content = re.sub(r'src="[^"]*placeholder[^"]*"', 'src="https://source.unsplash.com/random/800x600/?tech"', content)
            
        return content

    def _validate_code(self, content, filename):
        """
        Phase 3.1: Syntax Validation (Safety Net).
        Returns (bool, error_message).
        """
        ext = os.path.splitext(filename)[1]
        
        # PYTHON: Strict AST check
        if ext == ".py":
            try:
                import ast
                ast.parse(content)
                return True, ""
            except Exception as e:
                return False, str(e)
                
        # JS/CSS/JSON: Basic heuristic (Balanced Braces)
        # (Node check would be better, but this is fast and dependency-free)
        if ext in [".js", ".css", ".json", ".jsx", ".ts", ".tsx"]:
            # Filter out comments? Maybe too complex for regex.
            # Just count braces.
            open_b = content.count("{")
            close_b = content.count("}")
            if open_b != close_b:
                 return False, f"Unbalanced curly braces {{}}: {open_b} vs {close_b}"
                 
            open_p = content.count("(")
            close_p = content.count(")")
            if open_p != close_p:
                 return False, f"Unbalanced parentheses (): {open_p} vs {close_p}"
                 
        return True, ""

    def _repair_syntax_with_ollama(self, content, error_msg):
        """
        Phase 3.1: Auto-Repair broken code using Ollama.
        """
        brain = self.app.get('brain')
        if not brain: return content
        
        logger.info(f"🔧 Attempting Auto-Repair for syntax error: {error_msg}")
        
        prompt = f"""
The following code has a syntax error: "{error_msg}"

SOURCE CODE:
{content}

INSTRUCTION:
Fix the syntax error. Return ONLY the fixed code without markdown backticks.
"""
        try:
            fixed = brain.ask_local_ollama(prompt)
            if fixed:
                 # Clean potential markdown wrappers
                 fixed = re.sub(r'^```\w*\n', '', fixed)
                 fixed = re.sub(r'\n```$', '', fixed)
                 return fixed.strip()
        except:
            pass
            
        return content

    def _ensure_critical_files(self, matches, original_command):
        """
        Phase 3.4: Critical File Verification.
        If we are building a website but missing index.html, generate it.
        """
        filenames = [m[0] for m in matches]
        
        # Check if it looks like a web project (has css/js but no html)
        has_css_js = any(f.endswith(('.css', '.js')) for f in filenames)
        has_html = any(f.endswith('.html') for f in filenames)
        
        if has_css_js and not has_html:
            logger.warning("⚠️ MISSING CRITICAL FILE: index.html detected. Triggering emergency generation...")
            self.speech.speak("I noticed I missed the HTML file. Generating it now...")
            
            brain = self.app.get('brain')
            # Fallback to repair prompt
            # Create context from existing files
            css_content = next((m[1] for m in matches if m[0].endswith('.css')), "")
            js_content = next((m[1] for m in matches if m[0].endswith('.js')), "")
            
            prompt = f"""
CRITICAL ERROR: You generated CSS/JS but FORGOT the `index.html` file.
Generate the `index.html` file now.
It must link to the generated CSS/JS and implement the user request.

USER REQUEST: {original_command}

GENERATED CSS:
{css_content[:1500]}...

GENERATED JS:
{js_content[:1500]}...

OUTPUT FORMAT:
<file name="index.html">
... content ...
</file>
"""
            # Use main model for this critical logic task
            try:
                # Add simple timeout protection (though synchronous call depends on underlying lib)
                response = brain.generate_code(prompt, model="llama-3.3-70b-versatile")
                
                if response:
                    new_matches = re.findall(r'<file name="(.*?)">(.*?)</file>', response, re.DOTALL)
                    if new_matches:
                        logger.info(f"✅ Emergency generation successful. Added {len(new_matches)} files.")
                        matches.extend(new_matches)
                        return matches
            except Exception as e:
                logger.error(f"⚠️ Emergency generation failed: {e}")
                
            # FALLBACK: If Brain fails/times out, generate a minimal skeleton
            logger.error("⚠️ Brain unresponsive. Deploying minimal fallback HTML.")
            fallback_html = """<!DOCTYPE html>
<html>
<head>
    <title>Generated Site</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1>Site Generated (Emergency Mode)</h1>
        <p>The AI Architect encountered a neural block, but your styles/scripts were saved.</p>
        <p>Please ask Jarvis to "Refine the HTML" to fix this.</p>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
            matches.append(("index.html", fallback_html))
                    
        return matches
