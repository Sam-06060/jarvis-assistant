import json
import re
import time
import logging
import config
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

@dataclass
class Thought:
    reasoning: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None

@dataclass
class Observation:
    tool: str
    result: str
    success: bool

class AgentMaxIterationsError(Exception):
    """Raised when the agent exceeds the configured maximum iterations."""
    pass

class AgentCore:
    def __init__(self, registry, config: config.AgentConfig):
        self.registry = registry
        self.config = config
        self.brain = registry.get("brain")
        self.hud = registry.get("hud")
        
    def run(self, task: str) -> str:
        """
        Main entry point for task execution.
        Follows the ReAct Loop (Reason -> Act -> Observe).
        """
        history: List[str] = []
        iterations = 0
        
        # 🧠 Stage 6 Reset: Clear memory vault for new task
        commander = self.registry.get("commander")
        if commander and hasattr(commander, "memory_vault"):
            commander.memory_vault = {}

        system_context = self._get_system_context()
        system_prompt = self._build_system_prompt(system_context)
        
        try:
            while iterations < self.config.max_iterations:
                iterations += 1
                logger.info(f"🤖 Agent Iteration {iterations}/{self.config.max_iterations}")
                
                # 🚀 Stage 13: History Pruning (Keep Context + Last 20 turns)
                # Keep first 6 turns (Setup/Music Info) + transition + last 20 turns
                active_history = history
                if len(history) > 30:
                    active_history = history[:6] + ["... (intermediate loops pruned for context density) ..."] + history[-20:]

                # 1. REASON
                prompt = self._build_iteration_prompt(task, active_history)
                response = self.brain.ask(prompt, system_prompt=system_prompt, is_agentic=True)
                
                if not response:
                    return "I encountered an error while thinking, sir."
                
                # 2. PARSE
                try:
                    thought = self._parse_response(response)
                except Exception as parse_err:
                    # SELF-CORRECTION: Feed the parse error back to the model
                    logger.warning(f"⚠️ Agent Parse Error: {parse_err}")
                    history.append(f"Thought: {response[:100]}...")
                    history.append(f"Observation: [!] INVALID FORMAT. Error: {str(parse_err)}. Please follow the strict format: Thought, Checklist, Reasoning, Action, Action Input.")
                    continue

                self._stream_to_hud(thought)
                
                if not thought.action:
                    # Verify if a Final Answer is actually present
                    if "Final Answer:" in response:
                        return response.split("Final Answer:")[-1].strip()
                    else:
                        # If no action and no final answer, force a correction
                        history.append(f"Thought: {thought.reasoning}")
                        history.append("Observation: [!] You provided a Thought but no Action or Final Answer. Please provide a tool-call or a final conclusion.")
                        continue
                
                # 3. ACT
                observation = self._execute_action(thought)
                
                # 4. OBSERVE
                obs_result = observation.result
                # PRUNING: Only truncate if EXTREMELY long to avoid cutting critical data (like lyrics)
                if len(obs_result) > 5000:
                    obs_result = obs_result[:3000] + "\n... (excessive detail pruned) ...\n" + obs_result[-1000:]

                history.append(f"Thought: {thought.reasoning}")
                if "Checklist:" in response:
                     # Keep checklist in history for context
                     checklist = re.search(r"Checklist:(.*?)(?:\nReasoning:|$)", response, re.DOTALL)
                     if checklist: history[-1] = f"Checklist:{checklist.group(1)}\nReasoning: {thought.reasoning}"

                # REPEAT GUARD: prevent identical actions from clogging history 
                last_turn = history[-10:] # Check wider recent context
                action_str = f"Action: {thought.action} Input: {json.dumps(thought.action_input)}"
                
                # Count occurrences of this exact action or similar query
                repeat_count = 0
                for h in last_turn:
                    if action_str in h: repeat_count += 1
                    # Detect similar search queries even if keywords change slightly
                    if thought.action == "web_search" and "Action: web_search" in h:
                        old_query = re.search(r'"query": "(.*?)"', h)
                        if old_query and thought.action_input.get("query"):
                            # Simple fuzzy check: if 80% same words, it's a repeat
                            q1_words = set(thought.action_input["query"].lower().split())
                            q2_words = set(old_query.group(1).lower().split())
                            if len(q1_words & q2_words) / max(len(q1_words), 1) > 0.8:
                                repeat_count += 1

                if repeat_count >= 1:
                    logger.warning(f"⚠️ Agent Stall Detected: Repeat Action '{thought.action}' (Count: {repeat_count+1}).")
                    obs_result = f"[!] REPEAT DETECTED ({repeat_count+1}). You are stuck in a cycle. "
                    if thought.action == "web_search":
                        obs_result += "DO NOT search again for the same thing. You PROBABLY ALREADY HAVE the data in previous observations. If you fetched a URL, the lyrics/data ARE in that observation. PROVIDE THE FINAL ANSWER OR MOVE TO THE NEXT ITEM ON YOUR CHECKLIST."
                    else:
                        obs_result += "Change your input or provide a Final Answer based on available data."

                history.append(f"Action: {thought.action}")
                history.append(f"Action Input: {json.dumps(thought.action_input)}")
                history.append(f"Observation: {obs_result}")
                
                # If tool failed, the observation will contain "Error:" or "[!]"
                # The model will see this in the next iteration and retry.
                
            raise AgentMaxIterationsError("Hit iteration cap.")
            
        except AgentMaxIterationsError:
            error_msg = f"I've hit my planning limit of {self.config.max_iterations} steps for this task, sir. "
            # Try to summarize progress
            return error_msg + "I was able to determine that: " + (history[-1] if history else "I couldn't reach a conclusion.")
        except Exception as e:
            logger.error(f"❌ Agent Loop Error: {e}")
            return f"My apologies, sir. An error occurred in my agentic core: {str(e)}"

    def _build_system_prompt(self, context: str) -> str:
        commander = self.registry.get("commander")
        tools_desc = ""
        if hasattr(commander, "get_tools_description"):
            tools_desc = commander.get_tools_description()
        
        return f"""You are JARVIS, an autonomous agentic assistant. 
You solve complex multi-step tasks using a ReAct (Reasoning + Action) loop.

System Context:
{context}

Available Tools:
{tools_desc}

Strict Format:
Thought: I must first break down the user's request into a checklist.
Checklist:
- [ ] Task 1
- [ ] Task 2
Reasoning: I will now execute Task 1.
Action: tool_name
Action Input: {{ "param": "value" }}
--- OR ---
Thought: I have completed all items in my checklist.
Checklist:
- [x] Task 1
- [x] Task 2
Reasoning: Every part of the request is satisfied. I am ready to provide the final answer.
Final Answer: ...

Rules:
1. **CHECKLIST**: Use [ ] (pending) and [x] (completed) in Thought.
2. **NO-HALFS**: Final Answer only if ALL items are [x].
3. **VERIFY**: Before Final Answer, ask: "Satisfied all parts?"
4. **AMBIGUITY**: If unclear, ask for clarification in Final Answer. Don't guess.
5. **NO-HALLUCINATION**: Use ONLY listed tools. If missing, explain but don't call.
6. **NO-LOOP**: Stop if tool fails 3x with same error.
7. Output 1 Thought + 1 Action/Final Answer per turn. Use JSON for Action Input.
8. Ground completions in hard Evidence from Observations.
9. **DATA INCLUSION**: Your Final Answer MUST include the actual data retrieved (weather degrees, news titles, facts, etc.).
10. **STRICT JSON**: Your 'Action Input' MUST be valid JSON. Use double quotes for keys/values.
11. **NO REPETITION**: Never search the same query twice. If a search fails, try a different keyword or specialized site (e.g., Jina.ai for paywalls).
12. **FETCH FIRST**: Use 'fetch_url' on specific results rather than searching over and over.
13. **FINAL ANSWER PRIORITY**: Once you have the requested data (even if from just one site), STOP searching and provide the Final Answer. Do not strive for "perfect" exhaustive research.
14. **NO EXHAUSTIVE LOOPS**: Do not fetch more than 2-3 links for any single task. If you can't find it in 3 links, tell the user what you found and stop.
15. **DATA SUFFICIENCY**: If an observation contains a block of 10+ lines of text (like lyrics, news content, or a bio), assume you HAVE the data. Do not search for "full" or "complete" versions unless explicitly asked.
16. **TERMINATION REINFORCEMENT**: If you see "--- LYRICS DETECTED ---" in an observation, STOP ACTING and provide the Final Answer immediately.
"""

    def _build_iteration_prompt(self, task: str, history: List[str]) -> str:
        history_text = "\n".join(history)
        return f"User Task: {task}\n\nHistory:\n{history_text}\n\nNext Step:"

    def _parse_response(self, text: str) -> Thought:
        # Standard ReAct patterns - Resilient Regex
        thought_match = re.search(r"Thought:\s*(.*?)(?:\nChecklist:|\nReasoning:|\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        checklist_match = re.search(r"Checklist:\s*(.*?)(?:\nReasoning:|\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        reasoning_match = re.search(r"Reasoning:\s*(.*?)(?:\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(\w+)", text)
        
        reasoning = (reasoning_match.group(1).strip() if reasoning_match else 
                     thought_match.group(1).strip() if thought_match else "")
        
        # Robustness: If the model provides an Action or Final Answer but forgot the Reasoning prefix,
        # don't fail. We can infer the reasoning or just accept the action.
        action = action_match.group(1).strip() if action_match else None
        final_answer_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)

        if not reasoning and not action and not final_answer_match:
             raise ValueError("Missing 'Thought', 'Action', or 'Final Answer' block.")
        action_input = {}
        
        if action:
            # ROBUST JSON EXTRACTION: Search for the first '{' after Action and find matching '}'
            raw_input = ""
            action_pos = text.find(f"Action: {action}")
            if action_pos == -1: action_pos = text.find("Action:")
            
            start_idx = text.find("{", action_pos)
            if start_idx != -1:
                # Brace matching to handle trailing text or nested braces
                stack = 0
                for i in range(start_idx, len(text)):
                    if text[i] == '{': stack += 1
                    elif text[i] == '}':
                        stack -= 1
                        if stack == 0:
                            raw_input = text[start_idx:i+1]
                            break
            
            if raw_input:
                # HARDENING: Strip markdown blocks if the LLM wrapped it
                if "```" in raw_input:
                     raw_input = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", raw_input, flags=re.DOTALL).strip()
                
                try: 
                    action_input = json.loads(raw_input)
                except: 
                    # FALLBACK: Use ast.literal_eval for single-quoted Python-style dicts
                    # This is SAFER than .replace("'", '"') which breaks URLs with single quotes
                    try:
                        import ast
                        action_input = ast.literal_eval(raw_input)
                        logger.debug(f"🛠️ AgentCore: Recovered input via ast.literal_eval")
                    except Exception as e:
                        raise ValueError(f"Invalid JSON in Action Input: {raw_input[:100]}... (Error: {str(e)})")
            else:
                raise ValueError(f"Action '{action}' provided but 'Action Input' block is missing or malformed.")

        # Fallback for tool_call tags
        if not action and "<tool_call>" in text:
             xml_func = re.search(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL)
             if xml_func:
                 try:
                     parsed = json.loads(xml_func.group(1).strip())
                     action = parsed.get("name") or parsed.get("tool")
                     action_input = parsed.get("arguments") or parsed.get("parameters") or parsed
                 except: pass

        final_answer = None
        if "Final Answer:" in text:
            final_answer = text.split("Final Answer:")[1].strip()

        # The Thought dataclass does not have 'thought', 'checklist', 'final_answer' fields.
        # Mapping to existing fields:
        # 'thought' and 'reasoning' both map to 'reasoning'
        # 'checklist' is not directly stored in Thought, but can be part of reasoning if needed.
        # 'final_answer' is not directly stored in Thought, it's a return value of run().
        # So, we will stick to the original Thought dataclass structure.
        return Thought(reasoning=reasoning or "Thinking...", action=action, action_input=action_input)

    def _execute_action(self, thought: Thought) -> Observation:
        commander = self.registry.get("commander")
        if not hasattr(commander, "execute_tool"):
            return Observation(tool=thought.action, result="Tool system not initialized.", success=False)
        
        # 🛡️ Stage 8: Tool Name Validation (Anti-Hallucination)
        available_tools = commander.tools if hasattr(commander, "tools") else {}
        if thought.action not in available_tools:
            return Observation(
                tool=thought.action, 
                result=f"[!] ERROR: Tool '{thought.action}' does not exist. Please check the 'Available Tools' list in your system prompt and try a different tool.", 
                success=False
            )
        
        try:
            result = commander.execute_tool(thought.action, thought.action_input)
            return Observation(tool=thought.action, result=str(result), success=True)
        except Exception as e:
            return Observation(tool=thought.action, result=f"Error executing tool: {str(e)}", success=False)

    def _get_system_context(self) -> str:
        import os, platform, getpass
        home = os.path.expanduser("~")
        user = getpass.getuser()
        os_name = platform.system()
        user_email = getattr(config, "USER_EMAIL", "samson06060@gmail.com")
        return f"- Operating System: {os_name}\n- Current User: {user}\n- User Email: {user_email}\n- Home Directory: {home}\n- Desktop: {os.path.join(home, 'Desktop')}"

    def _stream_to_hud(self, thought: Thought):
        if self.hud:
            msg = f"💭 {thought.reasoning}"
            if thought.action:
                msg += f"\n🛠️ Using: {thought.action}"
            self.hud.put(("AGENT", msg))
