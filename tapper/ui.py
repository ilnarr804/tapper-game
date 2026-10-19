"""Графический интерфейс на Tkinter."""
import time
import tkinter as tk

from . import storage
from .logic import UPGRADES, GameState

BG = "#1e2433"
CARD = "#2a3247"
ACCENT = "#f5b942"
TEXT = "#e8ecf4"
MUTED = "#8b95ab"
AUTOSAVE_MS = 10_000
FRAME_MS = 100


def format_number(value: float) -> str:
    """1234 -> 1.2K, 1500000 -> 1.5M."""
    value = int(value)
    for limit, suffix in ((10**9, "B"), (10**6, "M"), (10**3, "K")):
        if value >= limit:
            return f"{value / limit:.1f}{suffix}"
    return str(value)


class TapperApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.state: GameState = storage.load()
        self.last_tick = time.monotonic()
        self.upgrade_buttons: dict[str, tk.Button] = {}

        root.title("Тапалка")
        root.geometry("420x640")
        root.configure(bg=BG)
        root.resizable(False, False)

        self._build_widgets()
        self._refresh()
        self.root.after(FRAME_MS, self._game_loop)
        self.root.after(AUTOSAVE_MS, self._autosave)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_widgets(self) -> None:
        self.coins_label = tk.Label(self.root, font=("Arial", 34, "bold"), fg=ACCENT, bg=BG)
        self.coins_label.pack(pady=(24, 0))
        tk.Label(self.root, text="монет", font=("Arial", 12), fg=MUTED, bg=BG).pack()

        self.stats_label = tk.Label(self.root, font=("Arial", 11), fg=TEXT, bg=BG)
        self.stats_label.pack(pady=(6, 14))

        self.tap_button = tk.Button(
            self.root, text="ТАП!", font=("Arial", 28, "bold"),
            fg="#1e2433", bg=ACCENT, activebackground="#ffd36e",
            relief="flat", bd=0, width=10, height=3, command=self._on_tap,
        )
        self.tap_button.pack(pady=8)

        self.float_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"), fg=ACCENT, bg=BG)
        self.float_label.pack()

        tk.Label(self.root, text="Улучшения", font=("Arial", 13, "bold"), fg=TEXT, bg=BG).pack(pady=(8, 4))
        shop = tk.Frame(self.root, bg=BG)
        shop.pack(fill="x", padx=20)
        for upgrade in UPGRADES:
            btn = tk.Button(
                shop, font=("Arial", 11), fg=TEXT, bg=CARD, activebackground="#38425e",
                activeforeground=TEXT, disabledforeground=MUTED, relief="flat", bd=0,
                pady=8, anchor="w", padx=12,
                command=lambda k=upgrade.key: self._on_buy(k),
            )
            btn.pack(fill="x", pady=3)
            self.upgrade_buttons[upgrade.key] = btn

        tk.Button(
            self.root, text="Сбросить прогресс", font=("Arial", 9), fg=MUTED, bg=BG,
            relief="flat", bd=0, command=self._on_reset,
        ).pack(side="bottom", pady=10)

    # ---- обработчики ----
    def _on_tap(self) -> None:
        gained = self.state.click()
        self.float_label.config(text=f"+{gained}")
        self.root.after(250, lambda: self.float_label.config(text=""))
        self._refresh()

    def _on_buy(self, key: str) -> None:
        self.state.buy(key)
        self._refresh()

    def _on_reset(self) -> None:
        self.state = GameState()
        storage.save(self.state)
        self._refresh()

    def _on_close(self) -> None:
        storage.save(self.state)
        self.root.destroy()

    # ---- циклы ----
    def _game_loop(self) -> None:
        now = time.monotonic()
        self.state.tick(now - self.last_tick)
        self.last_tick = now
        self._refresh()
        self.root.after(FRAME_MS, self._game_loop)

    def _autosave(self) -> None:
        storage.save(self.state)
        self.root.after(AUTOSAVE_MS, self._autosave)

    def _refresh(self) -> None:
        s = self.state
        self.coins_label.config(text=format_number(s.coins))
        self.stats_label.config(
            text=f"+{s.per_click} за тап  •  {format_number(s.per_second)}/сек  •  тапов: {s.total_clicks}"
        )
        for upgrade in UPGRADES:
            btn = self.upgrade_buttons[upgrade.key]
            level = s.levels[upgrade.key]
            effect = f"+{upgrade.click_bonus}/тап" if upgrade.click_bonus else f"+{upgrade.cps_bonus:g}/сек"
            btn.config(
                text=f"{upgrade.name}  (ур. {level})   {effect}   —   {format_number(s.cost(upgrade.key))}",
                state="normal" if s.can_buy(upgrade.key) else "disabled",
            )


def run() -> None:
    root = tk.Tk()
    TapperApp(root)
    root.mainloop()
