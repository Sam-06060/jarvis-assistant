# JARVIS

Production-ready local assistant stack for macOS:
- Python backend (`jarvis.py`) for voice, skills, automation, and AI orchestration
- Swift macOS app (`JarvisApp`) as desktop client
- Socket API bridge on port `8492`

This repo now includes a deterministic setup path so a fresh clone can run after following the guide below.

## Supported Platform
- macOS 13+
- Python 3.10+ (3.11 recommended)
- Xcode Command Line Tools (`xcode-select --install`)

## 1) Clone
```bash
git clone <(https://github.com/Sam-06060/jarvis-assistant.git)>
cd jarvis-assistant
```

## 2) Bootstrap Environment
Runtime only:
```bash
./scripts/bootstrap_macos.sh
```

Runtime + dev/test tools:
```bash
./scripts/bootstrap_macos.sh --dev
```

What this does:
- creates `.venv`
- installs dependencies
- creates `.env` from `.env.example` if missing
- creates runtime folders (`data`, `logs`, `macros`)

## 3) Configure `.env`
Edit `.env` and set real values:
- `PICOVOICE_API_KEY` (wake word)
- `OPENROUTER_API_KEY` (cloud conversation/code generation)

Optional keys:
- `PHONE_MAC_ADDRESS`
- `REFERENCE_IMAGE_PATH`

## 4) Preflight Check
Strict mode (recommended before first run):
```bash
.venv/bin/python scripts/doctor.py --strict
```

This validates:
- Python/OS compatibility
- required files and folders
- `.env` key readiness
- critical module imports
- API port availability (`8492`)

## 5) Build and Launch
Build app bundle:
```bash
cd JarvisApp
./build_app.sh
cd ..
```

Start backend + app:
```bash
./start_jarvis.sh
```

## Manual Backend Smoke Test
```bash
./test_backend.sh
```

## Permissions (macOS)
For full functionality, grant these when prompted:
- Microphone
- Camera
- Speech Recognition
- Accessibility
- Input Monitoring
- Contacts (optional but recommended)

If a permission was denied earlier, reset in System Settings and relaunch.

## Common Operations
Stop backend using port 8492:
```bash
lsof -tiTCP:8492 -sTCP:LISTEN | xargs kill
```

Run backend only:
```bash
.venv/bin/python jarvis.py --api
```

## Repo Hygiene Before GitHub Push
Recommended:
```bash
.venv/bin/python -m py_compile $(find . -name '*.py' -not -path './.venv/*')
.venv/bin/python scripts/doctor.py
```

The `.gitignore` is configured to exclude local/runtime artifacts (`.venv`, `logs`, `data`, etc.).

## Notes
- `scripts/doctor.py` is non-destructive and safe to run anytime.
- `start_jarvis.sh` is now portable (no machine-specific absolute paths).
- `JarvisApp/build_app.sh` is now portable (relative-path based).
