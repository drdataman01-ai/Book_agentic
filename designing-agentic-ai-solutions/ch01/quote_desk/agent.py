"""Harbor quote desk: Listings 1.2 and 1.4 of Chapter 1."""
import os
import sys
from pathlib import Path

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

MODEL = os.getenv("QUOTE_DESK_MODEL", "gemini-3.6-flash")
DISCOUNT_CAP = 0.15  # policy, enforced in code -- not in the prompt

SERVER = Path(__file__).resolve().parent.parent / "pricing_server" / "server.py"


def check_discount(requested_discount: float) -> dict:
    """Check a requested discount against Harbor's pricing policy.

    Args:
        requested_discount: The discount as a fraction, e.g. 0.18 for 18%.

    Returns:
        A dict with 'allowed' (bool), 'needs_manager' (bool) and 'reason'.
    """
    if requested_discount < 0:
        return {"allowed": False, "needs_manager": False,
                "reason": "Discount cannot be negative."}
    if requested_discount <= DISCOUNT_CAP:
        return {"allowed": True, "needs_manager": False,
                "reason": f"Within the {DISCOUNT_CAP:.0%} cap."}
    return {"allowed": True, "needs_manager": True,
            "reason": f"Above the {DISCOUNT_CAP:.0%} cap; manager approval required."}


INSTRUCTION = (
    "You help Harbor sales reps prepare quotes. "
    "Always call check_discount before discussing any discount. "
    "Use get_item_pricing for prices and stock, and check_margin for the margin. "
    "Never state a price or discount that did not come from a tool."
)

pricing_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable, args=[str(SERVER)]),
    ),
    tool_filter=["get_item_pricing", "check_margin"],
)

root_agent = Agent(
    name="quote_desk",
    model=MODEL,
    instruction=INSTRUCTION,
    tools=[check_discount, pricing_tools],
)
