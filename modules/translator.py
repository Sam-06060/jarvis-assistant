from deep_translator import GoogleTranslator as DeepGoogleTranslator
import re

class Translator:
    """Translate text using Google Translate (via deep-translator)"""
    
    def __init__(self):
        # deep-translator uses new instances for each translation typically, 
        # or we can keep a default one. We'll instantiate as needed.
        
        # Common language codes
        self.languages = {
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "portuguese": "pt",
            "russian": "ru",
            "japanese": "ja",
            "chinese": "zh-cn",
            "korean": "ko",
            "arabic": "ar",
            "hindi": "hi",
            "dutch": "nl",
            "swedish": "sv",
            "polish": "pl",
            "turkish": "tr",
            "greek": "el",
            "hebrew": "he",
            "thai": "th",
            "vietnamese": "vi",
            "indonesian": "id",
        }
    
    def translate(self, text, target_language, source_language="auto"):
        """Translate text to target language"""
        try:
            # Convert language name to code
            target_code = self.languages.get(target_language.lower(), target_language.lower())
            source_code = self.languages.get(source_language.lower(), source_language.lower())
            
            # Translate using deep-translator
            translator = DeepGoogleTranslator(source=source_code, target=target_code)
            result = translator.translate(text)
            
            if result:
                return f'"{text}" in {target_language}: "{result}"'
            else:
                return "Translation failed."
                
        except Exception as e:
            return f"Could not translate: {str(e)}"
    
    def detect_language(self, text):
        """Detect the language (Not fully supported in this version, returning placeholder)"""
        # validation of detection is tricky without a specific unexpected dependency or API key
        # For now we assume 'auto' source works for translation
        return "Language detection not implemented in this version."
    
    def parse_translation_command(self, command):
        """Parse natural language translation command"""
        command = command.lower()
        
        # Pattern: "translate hello to spanish"
        if "translate" in command:
            parts = command.split(" to ")
            if len(parts) == 2:
                text = parts[0].replace("translate", "").strip()
                target_lang = parts[1].strip()
                return self.translate(text, target_lang)
        
        # Pattern: "how do you say hello in spanish"
        # Pattern: "how to say hello in spanish"
        # Pattern: "what do you call hello in spanish"
        if any(phrase in command for phrase in ["how do you say", "how to say", "what do you call"]):
            # Extract text and language
            match = re.search(r'(?:how do you say|how to say|what do you call)\s+(.+?)\s+in\s+(\w+)', command)
            if match:
                text = match.group(1).strip()
                target_lang = match.group(2).strip()
                return self.translate(text, target_lang)
        
        return "Translation format: 'translate hello to spanish' or 'how do you say hello in spanish'"
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        langs = sorted(self.languages.keys())
        return "Supported languages: " + ", ".join(langs)