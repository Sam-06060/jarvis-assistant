import re
import math

class Calculator:
    """Perform calculations and unit conversions"""
    
    def __init__(self):
        self.conversion_factors = {
            # Length
            "kilometers_to_miles": 0.621371,
            "km_to_miles": 0.621371,
            "miles_to_kilometers": 1.60934,
            "miles_to_km": 1.60934,
            "meters_to_feet": 3.28084,
            "m_to_feet": 3.28084,
            "feet_to_meters": 0.3048,
            "feet_to_m": 0.3048,
            "centimeters_to_inches": 0.393701,
            "cm_to_inches": 0.393701,
            "inches_to_centimeters": 2.54,
            "inches_to_cm": 2.54,
            
            # Weight
            "kilograms_to_pounds": 2.20462,
            "kg_to_lbs": 2.20462,
            "kg_to_pounds": 2.20462,
            "pounds_to_kilograms": 0.453592,
            "lbs_to_kg": 0.453592,
            "pounds_to_kg": 0.453592,
            
            # Temperature (special case, not simple multiplication)
            # Celsius to Fahrenheit: (C × 9/5) + 32
            # Fahrenheit to Celsius: (F − 32) × 5/9
            
            # Volume
            "liters_to_gallons": 0.264172,
            "gallons_to_liters": 3.78541,
        }
    
    def calculate(self, expression):
        """Safely evaluate mathematical expression"""
        try:
            # Remove any potential dangerous operations
            expression = expression.lower()
            expression = expression.replace("^", "**")  # Allow ^ for power
            
            # Only allow numbers, operators, and safe functions
            allowed_chars = "0123456789+-*/().** "
            allowed_words = ["sqrt", "sin", "cos", "tan", "log", "abs", "round"]
            
            # Replace safe function names with math module equivalents
            for func in allowed_words:
                expression = expression.replace(func, f"math.{func}")
            
            # Check if expression is safe (only contains allowed characters)
            clean_expr = expression
            for func in allowed_words:
                clean_expr = clean_expr.replace(f"math.{func}", "")
            
            if not all(c in allowed_chars for c in clean_expr):
                return "Invalid expression. Only numbers and basic operators allowed."
            
            # Evaluate
            result = eval(expression, {"__builtins__": None}, {"math": math})
            
            # Format result
            if isinstance(result, float):
                if result.is_integer():
                    return f"Result: {int(result)}"
                else:
                    return f"Result: {result:.4f}"
            return f"Result: {result}"
            
        except Exception as e:
            return f"Could not calculate: {str(e)}"
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Convert temperature"""
        try:
            value = float(value)
            
            if from_unit.lower() in ["c", "celsius"] and to_unit.lower() in ["f", "fahrenheit"]:
                result = (value * 9/5) + 32
                return f"{value}°C = {result:.1f}°F"
            
            elif from_unit.lower() in ["f", "fahrenheit"] and to_unit.lower() in ["c", "celsius"]:
                result = (value - 32) * 5/9
                return f"{value}°F = {result:.1f}°C"
            
            else:
                return "Unsupported temperature conversion."
                
        except Exception as e:
            return f"Could not convert temperature: {str(e)}"
    
    def convert_unit(self, value, from_unit, to_unit):
        """Convert between units"""
        try:
            value = float(value)
            
            # Normalize unit names (handle plural, abbreviations, etc)
            unit_aliases = {
                'km': 'kilometers',
                'kilometers': 'kilometers',
                'kilometer': 'kilometers',
                'miles': 'miles',
                'mile': 'miles',
                'kg': 'kilograms',
                'kilograms': 'kilograms',
                'kilogram': 'kilograms',
                'lbs': 'pounds',
                'lb': 'pounds',
                'pounds': 'pounds',
                'pound': 'pounds',
                'm': 'meters',
                'meters': 'meters',
                'meter': 'meters',
                'ft': 'feet',
                'feet': 'feet',
                'foot': 'feet',
                'cm': 'centimeters',
                'centimeters': 'centimeters',
                'centimeter': 'centimeters',
                'inches': 'inches',
                'inch': 'inches',
                'in': 'inches',
            }
            
            from_unit = from_unit.lower().strip()
            to_unit = to_unit.lower().strip()
            
            # Normalize units
            from_normalized = unit_aliases.get(from_unit, from_unit)
            to_normalized = unit_aliases.get(to_unit, to_unit)
            
            # Check for temperature conversion
            if any(temp in from_unit for temp in ["celsius", "fahrenheit", "c", "f"]):
                return self.convert_temperature(value, from_unit, to_unit)
            
            # Build conversion key
            conversion_key = f"{from_normalized}_to_{to_normalized}"
            
            if conversion_key in self.conversion_factors:
                result = value * self.conversion_factors[conversion_key]
                return f"{value} {from_unit} = {result:.2f} {to_unit}"
            
            # Try reverse conversion
            reverse_key = f"{to_normalized}_to_{from_normalized}"
            if reverse_key in self.conversion_factors:
                result = value / self.conversion_factors[reverse_key]
                return f"{value} {from_unit} = {result:.2f} {to_unit}"
            
            return f"Conversion from {from_unit} to {to_unit} not supported."
            
        except Exception as e:
            return f"Could not convert: {str(e)}"
    
    def parse_and_calculate(self, command):
        """Parse natural language math command"""
        command = command.lower()
        
        # Check for conversions
        if "convert" in command:
            # Pattern: "convert 50 km to miles" or "convert 50 kilometers to miles"
            match = re.search(r'(\d+\.?\d*)\s*(km|kilometers|miles|kg|kilograms|pounds|lbs|celsius|fahrenheit|c|f|meters|feet|m|ft|inches|cm|centimeters)\s+to\s+(\w+)', command)
            if match:
                value = match.group(1)
                from_unit = match.group(2)
                to_unit = match.group(3)
                return self.convert_unit(value, from_unit, to_unit)
        
        # Always try to convert normalized math words to operators
        # Replace word operators with symbols
        expression = command
        for prefix in ["calculate", "what is", "what's", "compute"]:
            expression = expression.replace(prefix, "")
        
        # Convert words to operators
        expression = expression.replace("plus", "+")
        expression = expression.replace("add", "+")
        expression = expression.replace("minus", "-")
        expression = expression.replace("subtract", "-")
        expression = expression.replace("times", "*")
        expression = expression.replace("multiplied by", "*")
        expression = expression.replace("divided by", "/")
        # expression = expression.replace("and", "+")  # Too risky ("100 and 20" vs "finish and exit")
        
        expression = expression.strip()

        # Check for calculations - explicitly or if it looks like math now
        if any(word in command for word in ["calculate", "what is", "what's", "compute"]) or \
           any(op in expression for op in ["+", "-", "*", "/", "^"]):
            return self.calculate(expression)
        
        # Try to calculate directly if it looks like math
        if any(op in command for op in ["+", "-", "*", "/", "^"]):
            return self.calculate(command)
        
        return "I didn't understand the calculation. Try: 'calculate 5 + 3' or 'convert 50 km to miles'"
    
    def calculate_tip(self, amount, percentage=15):
        """Calculate tip amount"""
        try:
            amount = float(amount)
            percentage = float(percentage)
            
            tip = amount * (percentage / 100)
            total = amount + tip
            
            return f"Tip ({percentage}%): ${tip:.2f}\nTotal: ${total:.2f}"
            
        except Exception as e:
            return f"Could not calculate tip: {str(e)}"