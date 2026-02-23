# 🧞‍♂️ Jarvis Assistant - Feature List

A comprehensive list of capabilities for the Jarvis AI Assistant (v4.0 - Nuclear Build).

## 🚀 Core Technologies

### 1. Ultra-Fast Voice Engine
- **Hybrid Architecture**: Combines Apple Speech Recognition (Primary) + Faster Whisper (Fallback).
- **Latency**: **<200ms** response time (matches macOS dictation).
- **Smart Fallback**: Automatically switches to Whisper if Apple Speech fails.
- **VAD (Voice Activity Detection)**: Optimized 100ms silence detection for snappy interactions.
- **Privacy**: Fully on-device processing.

### 2. Advanced AI Brain
- **Local LLM**: Powered by **Llama 3.2** (running locally via Ollama).
- **Context Awareness**: Remembers conversation history and context.
- **Persona System**: "Iron Man" style personality with strict anti-hallucination rules.

### 3. Intelligent Web Search
- **AI-Powered Detection**: Uses a neural classifier (<500ms) to decide if a query needs live data.
- **No Hallucinations**: Fetches real-time info for factual questions ("Who is the PM?", "Stock price?").
- **Multi-Source**: Google Search, DuckDuckGo, and manual scraping fallback.

---

## � specialized Capabilities (The "Nuclear" Features)

### 🏗️ Architect Mode ("Build a app")
- **Project Scaffolding**: Can write entire coding projects from scratch.
- **Full Structure**: Generates folders, files, `main.py`, `requirements.txt` in one go.
- **Production Ready**: Uses best practices and modern standards.
- **Example**: "Build a Snake game in Python" -> Creates folder, writes code, launches it.

### 🎭 The Mimic ("Watch this")
- **Macro Recording**: Records mouse clicks, movements, and keyboard inputs.
- **Playback**: Replays complex tasks at variable speeds (1x, 2x, 0.5x).
- **Command**: "Watch this" (to record) -> "Mimic recent macro" (to replay).

### 🎓 Content Assassin ("Extract script")
- **YouTube Summarizer**: Downloads subtitles from a video URL.
- **Study Notes**: Generates a clean markdown summary of the video content.
- **Example**: "Analyze this https://youtube.com/..."

### 📡 Dead Drop ("Secure transfer")
- **Ironclad Transfer**: Securely uploads selected Finder files to ephemeral hosts (Oshi.at, PixelDrain).
- **Mobile Hand-off**: Generates a QR code in the terminal to download the file on your phone instantly.

### Cursor Control
- **Gesture Control**: Control mouse with hand gestures via webcam.
- **Gestures**: 
  - 👆 **Point**: Move cursor.
  - 👌 **Pinch**: Click/Drag.
  - ✊ **Fist**: Window Drag.
  - ✌️ **Peace**: Exit.
- **Fluid Movement**: Uses "One Euro Filter" for jitter-free, smooth tracking.

---

## �🛠️ System & Productivity Skills

### 💻 System Control
- **App Management**: "Open Spotify", "Close Chrome", "Focus Mode".
- **Hardware Control**: "Set volume to 50%", "Increase brightness".
- **Media Control**: Play/Pause, Next/Previous, Audio Ducking (lowers music when speaking).
- **Lock/Sleep**: "Lock my screen", "Go to sleep".

### 📅 Productivity
- **Alarms**: "Set an alarm for 7 AM" (integrates with macOS Clock).
- **Reminders**: "Remind me to buy milk".
- **Calendar**: "What's on my schedule?", "Add meeting tomorrow at 3pm".
- **Email**: Read and send emails.
- **Contacts**: Manage and query contacts.
- **Shortcuts**: Run any macOS Shortcut ("Run 'My Shortcut'").

### 🧰 Utilities
- **Calculator**: Natural language math ("What is 25 * 4?").
- **Weather**: Real-time updates ("What's the weather in Tokyo?").
- **News Service**: "Tell me the latest tech news".
- **Translator**: Translate text between languages.
- **Visuals**: "Hackerman mode" (System diagnostics animation).

---

## 🛡️ Security & Privacy

### FaceID Integration
- **Biometric Auth**: Verifies user identity before executing sensitive commands.
- **Local Storage**: Face data stored locally using `face_recognition`.

### Privacy First
- **Offline Capable**: Core features (Voice, Llama, Automation) work without internet.
- **Local Processing**: Voice, AI, and personal data stay on your Mac.

---

## 🧩 Architecture

- **Modular Design**: Plug-and-play "Skill" system for easy extension.
- **Standalone Modules**: Voice engine can be used in other projects.
- **Configuration**: Extensive `config.py` for customization.

---

*Verified as of February 2026*
