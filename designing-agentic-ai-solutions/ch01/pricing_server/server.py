"""A small MCP server exposing two pricing tools (Listing 1.3)."""
import csv
from pathlib import Path

from mcp.server.mcpserver import MCPServer

server = MCPServer("harbor-pricing")
ITEMS = {row["sku"]: row for row in
         csv.DictReader(open(Path(__file__).parent / "data" / "items.csv"))}


@server.tool()
def get_item_pricing(sku: str) -> dict:
    """Return list price, unit cost and units in stock for one SKU."""
    item = ITEMS.get(sku)
    if item is None:
        return {"found": False, "sku": sku}
    return {"found": True, "sku": sku,
            "list_price": float(item["list_price"]),
            "unit_cost": float(item["unit_cost"]),
            "in_stock": int(item["in_stock"])}


@server.tool()
def check_margin(sku: str, discount: float) -> dict:
    """Check whether a discount on a SKU keeps the margin above the 22% floor."""
    item = ITEMS[sku]
    price = float(item["list_price"]) * (1 - discount)
    margin = (price - float(item["unit_cost"])) / price
    return {"net_price": round(price, 2), "margin": round(margin, 4),
            "above_floor": margin >= 0.22}


if __name__ == "__main__":
    server.run()  # stdio transport by default
