import threading
def _prewarm_speech_imports():
    try:
        from modules.audio.recorder import AudioRecorder    
        from modules.audio.wakeword import WakeWordEngine   
        from modules.audio.transcriber import Transcriber   
    except Exception: pass

def _prewarm_brain_imports():
    try:
        from modules.brain import AIBrain                   
    except Exception: pass

def _prewarm_faceid_imports():
    try:
        import face_recognition                             
        import cv2                                          
        from modules.security import FaceID                
    except Exception: pass

def _prewarm_commands_imports():
    try:
        from modules.commands import CommandProcessor       
    except Exception: pass

_t1 = threading.Thread(target=_prewarm_speech_imports, daemon=True, name="Prewarm-Speech")
_t2 = threading.Thread(target=_prewarm_brain_imports, daemon=True, name="Prewarm-Brain")
_t3 = threading.Thread(target=_prewarm_faceid_imports, daemon=True, name="Prewarm-FaceID")
_t4 = threading.Thread(target=_prewarm_commands_imports, daemon=True, name="Prewarm-Cmd")

_t1.start()
_t2.start()
_t3.start()
_t4.start()
