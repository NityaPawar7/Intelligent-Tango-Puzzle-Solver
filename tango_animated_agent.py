"""
=============================================================================
 Tango Intelligent Agent - Backtracking Solver with Tkinter Animation
=============================================================================

PEAS specification
------------------
Performance Measure : Fill the Tango grid so every row/column has equal Suns
                      and Moons, with no three identical symbols adjacent.
Environment         : NxN Tango board - discrete, deterministic, fully
                      observable, static, single-agent.
Actuators           : place_symbol(row, col, symbol), remove_symbol(row, col)
Sensors             : Current partial grid state.

Search formulation
------------------
State Representation : 2D grid where '_' is empty, 'S' is Sun, 'M' is Moon.
Initial State        : Given partially filled puzzle.
Goal Test            : No empty cells remain and all constraints are valid.
Successor Function   : Pick the next empty cell and try Sun/Moon.
Search Strategy      : Depth-first search with chronological backtracking.

Run:
    python tango_animated_agent.py
=============================================================================
"""

import copy
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk


EMPTY = "_"
SUN = "S"
MOON = "M"
SYMBOLS = (SUN, MOON)

SUN_GLYPH = "\u2600"
MOON_GLYPH = "\u25d0"


INITIAL_GRID = [
    [SUN, EMPTY, EMPTY, EMPTY, MOON, EMPTY],
    [EMPTY, EMPTY, MOON, EMPTY, EMPTY, EMPTY],
    [EMPTY, SUN, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, SUN, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, MOON],
    [MOON, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
]


if sys.platform == "darwin":
    FONT = "Helvetica Neue"
    FONT_BOLD = "Helvetica Neue"
else:
    FONT = "Segoe UI"
    FONT_BOLD = "Segoe UI Semibold"


# =============================================================================
# 1. Agent / solver logic
# =============================================================================
class TangoAgent:
    """Goal-based Tango solver that emits events for a UI to animate."""

    def __init__(self, grid, on_event=None, stop_event=None):
        self.initial_grid = copy.deepcopy(grid)
        self.grid = copy.deepcopy(grid)
        self.n = len(grid)
        self.on_event = on_event or (lambda *args, **kwargs: None)
        self.stop_event = stop_event

        self.explored_states = 0
        self.backtracks = 0
        self.max_depth = 0
        self.assignments = 0
        self.solution = None

    def solve(self):
        solved = self._dfs(depth=0)
        return solved and self.solution is not None

    def _dfs(self, depth):
        if self.stop_event is not None and self.stop_event.is_set():
            return False

        self.max_depth = max(self.max_depth, depth)

        if self.is_goal(self.grid):
            self.solution = copy.deepcopy(self.grid)
            self._emit("solution", depth=depth)
            return True

        cell = self.select_unassigned_cell()
        if cell is None:
            return False

        row, col = cell
        for symbol in SYMBOLS:
            if self.stop_event is not None and self.stop_event.is_set():
                return False

            self.explored_states += 1
            self._emit("try", row=row, col=col, symbol=symbol, depth=depth)

            self.grid[row][col] = symbol
            if self.is_valid(self.grid):
                self.assignments += 1
                self._emit("place", row=row, col=col, symbol=symbol, depth=depth + 1)

                if self._dfs(depth + 1):
                    return True

                self.grid[row][col] = EMPTY
                self.backtracks += 1
                self._emit("remove", row=row, col=col, symbol=symbol, depth=depth)
            else:
                self._emit("conflict", row=row, col=col, symbol=symbol, depth=depth)
                self.grid[row][col] = EMPTY

        return False

    def select_unassigned_cell(self):
        """Use MRV: pick an empty cell with the fewest currently valid symbols."""
        best_cell = None
        best_options = None

        for row in range(self.n):
            for col in range(self.n):
                if self.grid[row][col] != EMPTY:
                    continue

                options = 0
                for symbol in SYMBOLS:
                    self.grid[row][col] = symbol
                    if self.is_valid(self.grid):
                        options += 1
                    self.grid[row][col] = EMPTY

                if best_options is None or options < best_options:
                    best_cell = (row, col)
                    best_options = options
                    if options == 0:
                        return best_cell

        return best_cell

    def is_goal(self, grid):
        return all(EMPTY not in row for row in grid) and self.is_valid(grid, complete=True)

    def is_valid(self, grid, complete=False):
        n = self.n
        half = n // 2

        for row in grid:
            if row.count(SUN) > half or row.count(MOON) > half:
                return False
            if complete and (row.count(SUN) != half or row.count(MOON) != half):
                return False

        for col in range(n):
            column = [grid[row][col] for row in range(n)]
            if column.count(SUN) > half or column.count(MOON) > half:
                return False
            if complete and (column.count(SUN) != half or column.count(MOON) != half):
                return False

        for row in range(n):
            for col in range(n - 2):
                if grid[row][col] != EMPTY and grid[row][col] == grid[row][col + 1] == grid[row][col + 2]:
                    return False

        for col in range(n):
            for row in range(n - 2):
                if grid[row][col] != EMPTY and grid[row][col] == grid[row + 1][col] == grid[row + 2][col]:
                    return False

        return True

    def _emit(self, kind, row=-1, col=-1, symbol=EMPTY, depth=0):
        filled = sum(cell != EMPTY for line in self.grid for cell in line)
        total = self.n * self.n
        self.on_event(
            kind,
            row=row,
            col=col,
            symbol=symbol,
            grid=copy.deepcopy(self.grid),
            depth=depth,
            progress=filled / total,
            explored=self.explored_states,
            backtracks=self.backtracks,
            assignments=self.assignments,
        )


# =============================================================================
# 2. GUI application
# =============================================================================
class TangoGUI:
    BG = "#101114"
    PANEL = "#1b1d23"
    PANEL_HL = "#252832"
    BORDER = "#343846"
    TEXT = "#f2f4f8"
    SUBTEXT = "#9aa3b2"
    MUTED = "#687082"

    SUN_COLOR = "#f7b731"
    MOON_COLOR = "#5dade2"
    SUCCESS = "#2ecc71"
    DANGER = "#e74c3c"
    WARN = "#f39c12"
    ACCENT = "#8e7cc3"

    CELL_EMPTY = "#f7f2e8"
    CELL_GIVEN = "#dfe7f3"
    CELL_TRY = "#fff0a6"
    CELL_PLACE = "#c9f5dc"
    CELL_CONFLICT = "#ffd0d8"
    CELL_REMOVE = "#eadcff"
    CELL_BORDER = "#1f2430"

    BOARD_PX = 540

    def __init__(self, root):
        self.root = root
        self.root.title("Tango Intelligent Agent")
        self.root.configure(bg=self.BG)
        self.root.geometry("1120x740")
        self.root.minsize(980, 680)

        self.initial_grid = copy.deepcopy(INITIAL_GRID)
        self.grid = copy.deepcopy(INITIAL_GRID)
        self.givens = {
            (r, c)
            for r, row in enumerate(self.initial_grid)
            for c, value in enumerate(row)
            if value != EMPTY
        }

        self.agent = None
        self.worker = None
        self.stop_event = threading.Event()
        self.event_queue = queue.Queue()

        self.delay_ms = 180
        self.running = False
        self.start_time = None
        self.timer_job = None
        self.flash = None
        self.current_try = None

        self._setup_styles()
        self._build_ui()
        self._draw_board()

        self.root.after(20, self._pump_events)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Tango.Horizontal.TScale",
            background=self.PANEL,
            troughcolor=self.PANEL_HL,
            sliderthickness=18,
        )
        style.configure(
            "Tango.Horizontal.TProgressbar",
            background=self.ACCENT,
            troughcolor=self.PANEL_HL,
            bordercolor=self.PANEL,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT,
            thickness=14,
        )

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=24, pady=(20, 6))

        tk.Label(
            header,
            text="Tango Intelligent Agent",
            bg=self.BG,
            fg=self.TEXT,
            font=(FONT_BOLD, 24),
        ).pack(side="left")
        tk.Label(
            header,
            text="  Backtracking search with animated reasoning",
            bg=self.BG,
            fg=self.SUBTEXT,
            font=(FONT, 11),
        ).pack(side="left", pady=(11, 0))

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=24, pady=(8, 12))
        body.grid_columnconfigure(0, weight=0, minsize=270)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=0, minsize=285)
        body.grid_rowconfigure(0, weight=1)

        self._build_controls(body)
        self._build_board(body)
        self._build_stats(body)

        self.status_var = tk.StringVar(value="Ready. Press Start to animate the Tango solver.")
        status = tk.Frame(self.root, bg=self.PANEL)
        status.pack(side="bottom", fill="x")
        tk.Label(
            status,
            textvariable=self.status_var,
            bg=self.PANEL,
            fg=self.SUBTEXT,
            font=(FONT, 10),
            anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=18, pady=8)

    def _build_controls(self, parent):
        panel = tk.Frame(parent, bg=self.PANEL)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        inner = tk.Frame(panel, bg=self.PANEL)
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            inner,
            text="CONTROLS",
            bg=self.PANEL,
            fg=self.SUBTEXT,
            font=(FONT, 9, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        self.start_btn = self._button(inner, "Start", self._on_start, "primary")
        self.start_btn.pack(fill="x", pady=(0, 8))
        self.stop_btn = self._button(inner, "Stop", self._on_stop, "danger")
        self.stop_btn.pack(fill="x", pady=(0, 8))
        self.reset_btn = self._button(inner, "Reset", self._on_reset, "neutral")
        self.reset_btn.pack(fill="x", pady=(0, 18))

        speed_line = tk.Frame(inner, bg=self.PANEL)
        speed_line.pack(fill="x", pady=(6, 2))
        tk.Label(
            speed_line,
            text="Animation Speed",
            bg=self.PANEL,
            fg=self.TEXT,
            font=(FONT, 10, "bold"),
        ).pack(side="left")
        self.speed_label_var = tk.StringVar(value=f"{self.delay_ms} ms / step")
        tk.Label(
            speed_line,
            textvariable=self.speed_label_var,
            bg=self.PANEL,
            fg=self.SUBTEXT,
            font=(FONT, 9),
        ).pack(side="right")

        self.speed_var = tk.IntVar(value=self.delay_ms)
        ttk.Scale(
            inner,
            from_=20,
            to=600,
            orient="horizontal",
            variable=self.speed_var,
            style="Tango.Horizontal.TScale",
            command=self._on_speed_change,
        ).pack(fill="x", pady=(6, 18))

        self.instant_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            inner,
            text="Instant solve",
            variable=self.instant_var,
            bg=self.PANEL,
            fg=self.TEXT,
            activebackground=self.PANEL,
            activeforeground=self.TEXT,
            selectcolor=self.PANEL_HL,
            font=(FONT, 10),
            bd=0,
            anchor="w",
        ).pack(fill="x")

        legend = tk.Frame(inner, bg=self.PANEL)
        legend.pack(fill="x", pady=(24, 0))
        tk.Label(
            legend,
            text="LEGEND",
            bg=self.PANEL,
            fg=self.SUBTEXT,
            font=(FONT, 9, "bold"),
        ).pack(anchor="w", pady=(0, 10))
        self._legend_item(legend, self.CELL_TRY, "Trying a symbol")
        self._legend_item(legend, self.CELL_PLACE, "Valid placement")
        self._legend_item(legend, self.CELL_CONFLICT, "Constraint conflict")
        self._legend_item(legend, self.CELL_REMOVE, "Backtracking")

        tk.Label(
            inner,
            text="Rules checked: equal Suns and Moons in every row/column, plus no three identical symbols together.",
            bg=self.PANEL,
            fg=self.MUTED,
            font=(FONT, 9),
            justify="left",
            wraplength=210,
        ).pack(anchor="w", pady=(24, 0))

        self._update_buttons()

    def _build_board(self, parent):
        wrap = tk.Frame(parent, bg=self.PANEL)
        wrap.grid(row=0, column=1, sticky="nsew")
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        holder = tk.Frame(wrap, bg=self.PANEL)
        holder.grid(row=0, column=0)

        self.canvas = tk.Canvas(
            holder,
            width=self.BOARD_PX + 42,
            height=self.BOARD_PX + 42,
            bg=self.PANEL,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=0, column=0, padx=24, pady=(24, 8))

        self.action_var = tk.StringVar(value="Waiting for the agent")
        tk.Label(
            holder,
            textvariable=self.action_var,
            bg=self.PANEL,
            fg=self.SUBTEXT,
            font=(FONT, 11),
        ).grid(row=1, column=0, pady=(0, 18))

    def _build_stats(self, parent):
        panel = tk.Frame(parent, bg=self.PANEL)
        panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        inner = tk.Frame(panel, bg=self.PANEL)
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            inner,
            text="TELEMETRY",
            bg=self.PANEL,
            fg=self.SUBTEXT,
            font=(FONT, 9, "bold"),
        ).pack(anchor="w")

        self.state_var = tk.StringVar(value="Idle")
        tk.Label(
            inner,
            textvariable=self.state_var,
            bg=self.PANEL,
            fg=self.WARN,
            font=(FONT_BOLD, 20),
            anchor="w",
        ).pack(anchor="w", pady=(10, 4))

        self.detail_var = tk.StringVar(value="Awaiting search")
        tk.Label(
            inner,
            textvariable=self.detail_var,
            bg=self.PANEL,
            fg=self.SUBTEXT,
            font=(FONT, 10),
            anchor="w",
            wraplength=230,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        self.stat_vars = {}
        self._stat_tile(inner, "states", "States Explored", "0")
        self._stat_tile(inner, "assignments", "Assignments", "0")
        self._stat_tile(inner, "backtracks", "Backtracks", "0")
        self._stat_tile(inner, "depth", "Search Depth", "0")
        self._stat_tile(inner, "time", "Elapsed Time", "0.000 s")

        tk.Label(
            inner,
            text="Completion",
            bg=self.PANEL,
            fg=self.TEXT,
            font=(FONT, 10, "bold"),
        ).pack(anchor="w", pady=(18, 4))
        self.progress = ttk.Progressbar(
            inner,
            mode="determinate",
            maximum=100,
            style="Tango.Horizontal.TProgressbar",
        )
        self.progress.pack(fill="x")

    def _button(self, parent, text, command, kind):
        palette = {
            "primary": (self.ACCENT, "white", "#7565a8"),
            "danger": (self.DANGER, "white", "#c74234"),
            "neutral": (self.PANEL_HL, self.TEXT, "#303440"),
        }
        bg, fg, hover = palette[kind]
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            bd=0,
            relief="flat",
            font=(FONT, 11, "bold"),
            padx=16,
            pady=10,
            cursor="hand2",
            disabledforeground="#777d8c",
        )

        def enter(_event):
            if str(button["state"]) == "normal":
                button.configure(bg=hover)

        def leave(_event):
            if str(button["state"]) == "normal":
                button.configure(bg=bg)

        button.bind("<Enter>", enter)
        button.bind("<Leave>", leave)
        return button

    def _legend_item(self, parent, color, text):
        row = tk.Frame(parent, bg=self.PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="  ", bg=color, width=2).pack(side="left")
        tk.Label(row, text=text, bg=self.PANEL, fg=self.SUBTEXT, font=(FONT, 9)).pack(
            side="left", padx=8
        )

    def _stat_tile(self, parent, key, label, value):
        tile = tk.Frame(parent, bg=self.PANEL_HL)
        tile.pack(fill="x", pady=5)
        tk.Label(
            tile,
            text=label,
            bg=self.PANEL_HL,
            fg=self.SUBTEXT,
            font=(FONT, 9),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 0))
        var = tk.StringVar(value=value)
        self.stat_vars[key] = var
        tk.Label(
            tile,
            textvariable=var,
            bg=self.PANEL_HL,
            fg=self.TEXT,
            font=(FONT_BOLD, 15),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 8))

    def _draw_board(self):
        self.canvas.delete("all")
        n = len(self.grid)
        margin = 20
        cell = self.BOARD_PX / n

        self.canvas.create_rectangle(
            margin - 2,
            margin - 2,
            margin + self.BOARD_PX + 2,
            margin + self.BOARD_PX + 2,
            fill=self.CELL_BORDER,
            outline=self.CELL_BORDER,
        )

        for row in range(n):
            for col in range(n):
                x1 = margin + col * cell
                y1 = margin + row * cell
                x2 = x1 + cell
                y2 = y1 + cell

                fill = self._cell_color(row, col)
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline=self.CELL_BORDER,
                    width=2,
                )

                value = self.grid[row][col]
                if value != EMPTY:
                    self._draw_symbol(x1, y1, x2, y2, value, (row, col) in self.givens)

    def _cell_color(self, row, col):
        if self.flash is not None and self.flash[1] == row and self.flash[2] == col:
            kind = self.flash[0]
            return {
                "place": self.CELL_PLACE,
                "conflict": self.CELL_CONFLICT,
                "remove": self.CELL_REMOVE,
            }.get(kind, self.CELL_EMPTY)

        if self.current_try == (row, col):
            return self.CELL_TRY
        if (row, col) in self.givens:
            return self.CELL_GIVEN
        return self.CELL_EMPTY

    def _draw_symbol(self, x1, y1, x2, y2, value, given):
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        size = max(28, int((x2 - x1) * 0.45))
        glyph = SUN_GLYPH if value == SUN else MOON_GLYPH
        color = self.SUN_COLOR if value == SUN else self.MOON_COLOR
        outline = "#8a6d1c" if value == SUN else "#1e5d87"

        self.canvas.create_oval(
            x1 + 12,
            y1 + 12,
            x2 - 12,
            y2 - 12,
            fill="#fffaf0" if value == SUN else "#eef7ff",
            outline=outline if given else color,
            width=3 if given else 2,
        )
        self.canvas.create_text(
            cx,
            cy,
            text=glyph,
            fill=color,
            font=(FONT_BOLD, size),
        )

    def _on_start(self):
        if self.running:
            return

        if not TangoAgent(self.initial_grid).is_valid(self.initial_grid):
            messagebox.showerror("Invalid Puzzle", "The starting grid already violates Tango rules.")
            return

        self.grid = copy.deepcopy(self.initial_grid)
        self.stop_event.clear()
        self.event_queue = queue.Queue()
        self.agent = TangoAgent(self.grid, on_event=self._queue_event, stop_event=self.stop_event)
        self.worker = threading.Thread(target=self._run_agent, daemon=True)

        self.running = True
        self.start_time = time.time()
        self.state_var.set("Searching")
        self.detail_var.set("The agent is exploring valid Sun/Moon placements.")
        self.status_var.set("Search running...")
        self._update_buttons()
        self._tick_timer()
        self.worker.start()

    def _run_agent(self):
        solved = self.agent.solve()
        self.event_queue.put(("done", {"solved": solved, "solution": self.agent.solution}))

    def _queue_event(self, kind, **payload):
        self.event_queue.put((kind, payload))
        if not self.instant_var.get():
            time.sleep(self.delay_ms / 1000)

    def _pump_events(self):
        processed = 0
        max_events = 500 if self.instant_var.get() else 8

        while processed < max_events:
            try:
                kind, payload = self.event_queue.get_nowait()
            except queue.Empty:
                break
            self._handle_event(kind, payload)
            processed += 1

        self.root.after(20, self._pump_events)

    def _handle_event(self, kind, payload):
        if kind == "done":
            self._finish(payload["solved"], payload["solution"])
            return

        self.grid = payload["grid"]
        row = payload["row"]
        col = payload["col"]
        symbol = payload["symbol"]
        self.current_try = None
        self.flash = None

        if kind == "try":
            self.current_try = (row, col)
            self.action_var.set(f"Trying {self._name(symbol)} at row {row + 1}, column {col + 1}")
            self.detail_var.set("Checking row, column, and three-in-a-row constraints.")
        elif kind == "place":
            self.flash = ("place", row, col)
            self.action_var.set(f"Placed {self._name(symbol)} at row {row + 1}, column {col + 1}")
            self.detail_var.set("Placement accepted. The agent moves deeper.")
        elif kind == "conflict":
            self.flash = ("conflict", row, col)
            self.action_var.set(f"Rejected {self._name(symbol)} at row {row + 1}, column {col + 1}")
            self.detail_var.set("That move violates at least one Tango rule.")
        elif kind == "remove":
            self.flash = ("remove", row, col)
            self.action_var.set(f"Backtracking from row {row + 1}, column {col + 1}")
            self.detail_var.set("No valid continuation was found from this branch.")
        elif kind == "solution":
            self.state_var.set("Solved")
            self.detail_var.set("A complete valid Tango board has been found.")

        self.stat_vars["states"].set(str(payload["explored"]))
        self.stat_vars["assignments"].set(str(payload["assignments"]))
        self.stat_vars["backtracks"].set(str(payload["backtracks"]))
        self.stat_vars["depth"].set(str(payload["depth"]))
        self.progress["value"] = int(payload["progress"] * 100)
        self._draw_board()

    def _finish(self, solved, solution):
        self.running = False
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        if solved and solution:
            self.grid = solution
            self.state_var.set("Solved")
            self.detail_var.set("The final board satisfies all Tango constraints.")
            self.status_var.set("Solved successfully.")
            self.action_var.set("Solution complete")
            self.progress["value"] = 100
        else:
            self.state_var.set("Stopped" if self.stop_event.is_set() else "No solution")
            self.detail_var.set("Search stopped before completion." if self.stop_event.is_set() else "No valid board exists.")
            self.status_var.set(self.detail_var.get())
            self.action_var.set(self.state_var.get())

        self.current_try = None
        self.flash = None
        self._draw_board()
        self._update_buttons()

    def _on_stop(self):
        if self.running:
            self.stop_event.set()
            self.status_var.set("Stopping after the current step...")

    def _on_reset(self):
        if self.running:
            self._on_stop()
        self.grid = copy.deepcopy(self.initial_grid)
        self.current_try = None
        self.flash = None
        self.state_var.set("Idle")
        self.detail_var.set("Awaiting search")
        self.action_var.set("Waiting for the agent")
        self.status_var.set("Ready. Press Start to animate the Tango solver.")
        self.progress["value"] = 0
        for key, value in {
            "states": "0",
            "assignments": "0",
            "backtracks": "0",
            "depth": "0",
            "time": "0.000 s",
        }.items():
            self.stat_vars[key].set(value)
        self._draw_board()
        self._update_buttons()

    def _on_speed_change(self, _value):
        self.delay_ms = int(float(self.speed_var.get()))
        self.speed_label_var.set(f"{self.delay_ms} ms / step")

    def _tick_timer(self):
        if not self.running or self.start_time is None:
            return
        elapsed = time.time() - self.start_time
        self.stat_vars["time"].set(f"{elapsed:.3f} s")
        self.timer_job = self.root.after(100, self._tick_timer)

    def _update_buttons(self):
        self.start_btn.configure(state="disabled" if self.running else "normal")
        self.stop_btn.configure(state="normal" if self.running else "disabled")
        self.reset_btn.configure(state="normal")

    def _name(self, symbol):
        return "Sun" if symbol == SUN else "Moon"

    def _on_close(self):
        self.stop_event.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    TangoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
