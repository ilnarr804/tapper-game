"""Игровая логика. Не зависит от интерфейса, поэтому легко тестируется."""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class UpgradeDef:
    key: str
    name: str
    base_cost: int
    growth: float       # во сколько раз дорожает каждый следующий уровень
    click_bonus: int    # прибавка к монетам за клик на каждый уровень
    cps_bonus: float    # прибавка к монетам в секунду на каждый уровень


UPGRADES = [
    UpgradeDef("finger", "Сильный палец", 10, 1.15, click_bonus=1, cps_bonus=0),
    UpgradeDef("auto", "Автокликер", 50, 1.15, click_bonus=0, cps_bonus=1),
    UpgradeDef("farm", "Монетная ферма", 300, 1.18, click_bonus=0, cps_bonus=6),
    UpgradeDef("factory", "Фабрика", 2000, 1.20, click_bonus=0, cps_bonus=40),
]
UPGRADES_BY_KEY = {u.key: u for u in UPGRADES}


class GameState:
    def __init__(self):
        self.coins: float = 0.0
        self.total_clicks: int = 0
        self.levels: dict[str, int] = {u.key: 0 for u in UPGRADES}

    # ---- вычисляемые значения ----
    @property
    def per_click(self) -> int:
        return 1 + sum(UPGRADES_BY_KEY[k].click_bonus * lvl for k, lvl in self.levels.items())

    @property
    def per_second(self) -> float:
        return sum(UPGRADES_BY_KEY[k].cps_bonus * lvl for k, lvl in self.levels.items())

    def cost(self, key: str) -> int:
        """Цена следующего уровня улучшения."""
        upgrade = UPGRADES_BY_KEY[key]
        return math.ceil(upgrade.base_cost * upgrade.growth ** self.levels[key])

    def can_buy(self, key: str) -> bool:
        return self.coins >= self.cost(key)

    # ---- действия ----
    def click(self) -> int:
        """Один тап. Возвращает, сколько монет получено."""
        gained = self.per_click
        self.coins += gained
        self.total_clicks += 1
        return gained

    def buy(self, key: str) -> bool:
        """Покупка улучшения. False — если не хватает монет."""
        if not self.can_buy(key):
            return False
        self.coins -= self.cost(key)
        self.levels[key] += 1
        return True

    def tick(self, seconds: float) -> None:
        """Пассивный доход за прошедшее время."""
        self.coins += self.per_second * seconds

    # ---- сохранение ----
    def to_dict(self) -> dict:
        return {"coins": self.coins, "total_clicks": self.total_clicks, "levels": dict(self.levels)}

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        state = cls()
        state.coins = float(data.get("coins", 0))
        state.total_clicks = int(data.get("total_clicks", 0))
        for key, lvl in data.get("levels", {}).items():
            if key in state.levels:
                state.levels[key] = int(lvl)
        return state
