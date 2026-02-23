import time
import datetime
import psutil
import random
from queue import Empty
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich import box
from rich.align import Align

# --- CONFIGURATION ---
THEME_COLOR = "cyan"
ACCENT_COLOR = "gold1"  # Iron Man Gold
WARNING_COLOR = "red"

class IronManHUD:
    def __init__(self, queue):
        self.queue = queue
        self.console = Console()
        self.layout = Layout()
        
        # State
        self.status_header = "INITIALIZING"
        self.status_detail = "System Boot..."
        self.conversation_log = []
        self.max_log_lines = 8
        self.start_time = time.time()
        
        # Animation states
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.spinner_idx = 0
        
        # Initialize Layout
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="left_panel", ratio=2),
            Layout(name="right_panel", ratio=1)
        )

    def get_time_display(self):
        now = datetime.datetime.now()
        return f"{now.strftime('%H:%M:%S')} | {now.strftime('%d-%b-%Y').upper()}"

    def get_system_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        batt = psutil.sensors_battery()
        batt_pct = batt.percent if batt else 0
        is_plugged = "⚡" if batt and batt.power_plugged else ""
        
        table = Table.grid(expand=True)
        table.add_column(style=THEME_COLOR)
        table.add_column(justify="right", style=ACCENT_COLOR)
        table.add_row("CPU CORE", f"{cpu}%")
        table.add_row("MEM ALLOC", f"{ram}%")
        table.add_row("PWR CELL", f"{batt_pct}% {is_plugged}")
        
        return Panel(table, title="[bold]SYSTEM VITALS[/bold]", border_style=THEME_COLOR, box=box.ROUNDED)

    def get_frequency_visualizer(self):
        bars = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        if self.status_header in ["LISTENING", "SPEAKING"]:
            visual = "".join(random.choice(bars) for _ in range(20))
            color = ACCENT_COLOR if self.status_header == "LISTENING" else THEME_COLOR
        else:
            visual = "─" * 20
            color = "dim " + THEME_COLOR
            
        return Panel(Align.center(Text(visual, style=color)), title="[bold]AUDIO WAVEFORM[/bold]", border_style=THEME_COLOR, box=box.ROUNDED)

    def get_status_panel(self):
        spin = self.spinner_chars[self.spinner_idx % len(self.spinner_chars)]
        self.spinner_idx += 1
        color = THEME_COLOR
        if self.status_header == "ERROR": color = WARNING_COLOR
        if self.status_header == "LISTENING": color = ACCENT_COLOR
        if self.status_header == "OFFLINE": color = "grey50"

        content = f"{spin}  {self.status_header}  >>  {self.status_detail}"
        return Panel(Align.center(Text(content, style=f"bold {color}")), border_style=color, box=box.HEAVY)

    def get_conversation_panel(self):
        chat_text = Text()
        visible_log = self.conversation_log[-self.max_log_lines:]
        for speaker, msg in visible_log:
            if speaker == "USER":
                chat_text.append(" COMMAND >> ", style=f"bold {ACCENT_COLOR}")
                chat_text.append(f"{msg}\n", style="white")
            elif speaker == "JARVIS":
                chat_text.append(" RESPONSE >> ", style=f"bold {THEME_COLOR}")
                chat_text.append(f"{msg}\n", style=THEME_COLOR)
            elif speaker == "SYS":
                chat_text.append(" SYSTEM >> ", style="dim white")
                chat_text.append(f"{msg}\n", style="dim white")
        
        return Panel(chat_text, title="[bold]DATA STREAM[/bold]", border_style=THEME_COLOR, box=box.ROUNDED, padding=(1, 2))

    def get_header_panel(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        uptime = int(time.time() - self.start_time)
        m, s = divmod(uptime, 60)
        h, m = divmod(m, 60)
        
        grid.add_row(
            Text(f" T+{h:02}:{m:02}:{s:02}", style="dim cyan"),
            Text("J.A.R.V.I.S.  INTERFACE", style=f"bold {THEME_COLOR}"),
            Text(f"{self.get_time_display()} ", style="dim cyan")
        )
        return Panel(grid, style=f"on {THEME_COLOR} black", box=box.SIMPLE)

    def update_data(self):
        try:
            while not self.queue.empty():
                msg_type, content = self.queue.get_nowait()
                if msg_type in ["IDLE", "LISTENING", "PROCESSING", "SPEAKING", "BOOTING", "ERROR", "OFFLINE", "SECURITY"]:
                    self.status_header = msg_type
                    self.status_detail = content
                elif msg_type == "USER":
                    self.conversation_log.append(("USER", content))
                elif msg_type == "JARVIS":
                    self.conversation_log.append(("JARVIS", content))
                elif msg_type == "LOG":
                    self.conversation_log.append(("SYS", content))
        except Empty: pass

    def render_loop(self):
        with Live(self.layout, refresh_per_second=10, screen=True) as live:
            while True:
                self.update_data()
                self.layout["header"].update(self.get_header_panel())
                self.layout["footer"].update(self.get_status_panel())
                self.layout["left_panel"].update(self.get_conversation_panel())
                
                right_col = Layout()
                right_col.split(Layout(self.get_system_stats(), ratio=1), Layout(self.get_frequency_visualizer(), ratio=1))
                self.layout["right_panel"].update(right_col)
                
                if self.status_header == "OFFLINE":
                    time.sleep(2)
                    break
                time.sleep(0.1)

def run_hud_process(queue):
    hud = IronManHUD(queue)
    hud.render_loop()