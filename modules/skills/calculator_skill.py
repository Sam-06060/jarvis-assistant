from .base import Skill
import re

class CalculatorSkill(Skill):
    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        cmd_len = len(cmd)

        # Guard: avoid hijacking long natural-language paragraphs.
        # These often contain punctuation/slashes/numbers but are not math commands.
        if cmd_len > 180 and not any(t in cmd for t in ["calculate", "compute", "math", "convert", "tip"]):
            return False

        math_triggers = ["calculate", "compute", "math", "convert", "tip"]
        if any(t in cmd for t in math_triggers):
            return True
        
        # "What is X + Y" or direct "5 + 5"
        ops = ["+", "-", "*", "/", "plus", "minus", "times", "divided", "dollars", "euros", "currency"]
        if any(op in cmd for op in ops):
             # Check for digits OR "what is"
             if any(char.isdigit() for char in cmd) or "what" in cmd or "how much" in cmd:
                 return True
             
        return False

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        calc = self.app.get('calculator')
        if not calc: return False

        # 1. Standard Math
        try:
             # Match can_handle logic: keywords OR direct math operators
             math_ops = ["+", "-", "*", "/", "plus", "minus", "times", "divided"]
             if any(word in cmd for word in ["calculate", "compute", "math", "what is", "what's"]) or \
                any(op in cmd for op in math_ops):
                 result = calc.parse_and_calculate(cmd)
                 self.speech.speak(result)
                 self.log_usage(command)
                 return True
        except ZeroDivisionError:
             self.speech.speak("I cannot divide by zero.")
             return True
        except (SyntaxError, ValueError):
             self.speech.speak("I didn't understand that mathematical expression.")
             return True
        except Exception as e:
             self.logger.error(f"Calculator error: {e}")
             self.speech.speak("I had trouble calculating that.")
             return True
        
        # 2. Conversions
        if "convert" in cmd and any(unit in cmd for unit in ["km", "kilometers", "miles", "kg", "pounds", "celsius", "fahrenheit", "meters", "feet"]):
            result = calc.parse_and_calculate(cmd)
            self.speech.speak(result)
            return True
        
        # 3. Tip Calculator
        if "tip" in cmd and any(char.isdigit() for char in cmd):
            match = re.search(r'(\d+\.?\d*)', cmd)
            if match:
                amount = match.group(1)
                result = calc.calculate_tip(amount)
                self.speech.speak(result)
                return True
                
        return False
