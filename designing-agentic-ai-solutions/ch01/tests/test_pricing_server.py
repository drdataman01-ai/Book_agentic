"""Tests for the pricing server. No model and no network involved."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pricing_server"))
import server  # noqa: E402


def test_known_sku():
    r = server.get_item_pricing("BV-316-3")
    assert r == {"found": True, "sku": "BV-316-3", "list_price": 182.5,
                 "unit_cost": 121.0, "in_stock": 240}


def test_unknown_sku_is_not_an_error():
    assert server.get_item_pricing("NOPE") == {"found": False, "sku": "NOPE"}


def test_margin_at_12_percent_is_above_floor():
    r = server.check_margin("BV-316-3", 0.12)
    assert r["net_price"] == 160.6 and r["above_floor"] is True


def test_margin_at_18_percent_is_below_floor():
    r = server.check_margin("BV-316-3", 0.18)
    assert r["above_floor"] is False
