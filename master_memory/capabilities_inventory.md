# Capabilities Inventory (Skills & Tools)

Jarvis possesses a wide array of "Physical" tools (Python-based actions) and "Cognitive" playbooks (expert guidelines).

## Core Tools (Actionable)
| Tool Name | Category | Description |
| :--- | :--- | :--- |
| `get_market_data` | Market | Live prices for stocks, crypto, gold, etc. (via `yfinance`). |
| `web_search` | Research | Real-time internet search (DuckDuckGo/Google). |
| `fetch_url` | Research | Scrapes full text from a specific webpage. |
| `run_command` | System | Executes bash commands natively on macOS. |
| `write_file` / `finalize_project` | Filesystem | Sandbox-aware file creation and project deployment. |
| `control_ac` | IoT | Controls Samsung AC via SmartThings. |
| `manage_reminders` / `manage_alarms` | Productivity | Native macOS reminder and alarm management. |
| `manage_calendar` | Productivity | iCloud/macOS calendar event management. |
| `send_whatsapp` / `send_email` | Communication | Messaging via WhatsApp (Web) and Mail.app. |
| `cursor_control` | CV | Hand-gesture based mouse control (via MediaPipe). |
| `clipboard` | System | Reads/Writes to the macOS global clipboard. |
| `remember_fact` / `recall_fact` | Memory | Long-term persistent knowledge storage. |

## Expert Playbooks (Cognitive)
Jarvis has access to **2200+ playbooks** via `search_awesome_skills`. Notable categories include:
- **Development**: `saas-architect`, `react-patterns`, `supabase-automation`, `production-code-audit`.
- **Operations**: `cloud-devops`, `network-engineer`, `observability-engineer`.
- **Design**: `antigravity-design-expert`, `mobile-design`, `ui-ux-pro-max`.
- **Security**: `bug-hunter`, `pentest-checklist`, `xss-html-injection`.
- **Productivity**: `task-intelligence`, `kaizen`, `planning-with-files`.

## Tool Tiering
- **Tier 1 (Auto-Run)**: Read-only or safe actions (e.g., `get_weather`, `get_time`).
- **Tier 2 (Confirmation Required)**: Side-effecting actions (e.g., `send_email`, `delete_file`, `run_command`).
