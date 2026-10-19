import json

from tapper.logic import GameState
from tapper import storage


def test_click_adds_coins():
    state = GameState()
    state.click()
    assert state.coins == 1
    assert state.total_clicks == 1


def test_cannot_buy_without_coins():
    state = GameState()
    assert state.buy("finger") is False
    assert state.levels["finger"] == 0


def test_buy_finger_increases_click_power():
    state = GameState()
    state.coins = 100
    assert state.buy("finger") is True
    assert state.per_click == 2
    assert state.coins == 90  # цена 10


def test_cost_grows_with_level():
    state = GameState()
    first = state.cost("auto")
    state.coins = 1000
    state.buy("auto")
    assert state.cost("auto") > first


def test_passive_income():
    state = GameState()
    state.coins = 100
    state.buy("auto")        # +1/сек
    before = state.coins
    state.tick(10)
    assert state.coins == before + 10


def test_save_and_load_roundtrip(tmp_path):
    state = GameState()
    state.coins = 500
    state.buy("finger")
    state.click()
    path = tmp_path / "save.json"
    storage.save(state, path)
    loaded = storage.load(path)
    assert loaded.coins == state.coins
    assert loaded.levels == state.levels
    assert loaded.total_clicks == state.total_clicks


def test_load_missing_file_gives_new_game(tmp_path):
    assert storage.load(tmp_path / "nope.json").coins == 0


def test_load_corrupted_file_gives_new_game(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{ not json", encoding="utf-8")
    assert storage.load(path).coins == 0
