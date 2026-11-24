"""Returns MCP server for Cymbal Home & Garden (Chapter 5), abridged.

Task-shaped tools; identity from the verified access token, never from
arguments; enumerated inputs; refund policy enforced here, once;
idempotent writes; structured, actionable errors.
"""
from datetime import date, timedelta
from typing import Literal

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from cymbal.orders import find_order, returns_store

server = MCPServer("cymbal-returns")    # token verifier and auth settings: see repo

RETURN_WINDOW = timedelta(days=90)
AUTO_REFUND_LIMIT = 150.00              # above this, a person must approve
Reason = Literal["damaged", "defective", "wrong_item", "not_needed", "late"]


def current_customer_id() -> str:
    token = get_access_token()          # set by the server's auth middleware
    if token is None or not token.subject:
        raise PermissionError("No authenticated customer on this request.")
    return token.subject


def _error(code: str, message: str, next_step: str) -> dict:
    return {"ok": False, "error": code, "message": message, "next_step": next_step}


@server.tool(annotations=ToolAnnotations(read_only_hint=True))
def get_return_options(order_number: str) -> dict:
    """List the lines of one of the customer's orders that can be returned.

    Use this before start_return. Returns at most 20 lines, each with
    line_id, product name, quantity, price and the last return date.
    """
    order = find_order(order_number, customer_id=current_customer_id())
    if order is None:
        return _error("ORDER_NOT_FOUND", "No order with that number for this customer.",
                      "Ask the customer to check the order number.")
    lines = [
        {"line_id": l.id, "product": l.name, "qty": l.qty, "price": l.price,
         "return_by": (l.delivered + RETURN_WINDOW).isoformat()}
        for l in order.lines
        if l.delivered and date.today() <= l.delivered + RETURN_WINDOW
    ][:20]
    return {"ok": True, "order_number": order_number, "returnable_lines": lines}


@server.tool(annotations=ToolAnnotations(destructive_hint=False, idempotent_hint=True))
def start_return(order_number: str, line_id: str, quantity: int,
                 reason: Reason, idempotency_key: str) -> dict:
    """Start a return for one order line and say what happens next.

    Refunds up to $150 are approved automatically; larger ones are queued
    for a person and the customer should expect an answer within one day.
    Safe to retry with the same idempotency_key.
    """
    customer = current_customer_id()
    if (done := returns_store.get(idempotency_key)) is not None:
        return done                                  # repeat call, same result
    order = find_order(order_number, customer_id=customer)
    line = order and next((l for l in order.lines if l.id == line_id), None)
    if not line:
        return _error("LINE_NOT_FOUND", "That item is not on this customer's order.",
                      "Call get_return_options and use a listed line_id.")
    if not 1 <= quantity <= line.qty:
        return _error("BAD_QUANTITY", f"Quantity must be 1 to {line.qty}.",
                      "Confirm the quantity with the customer.")
    if not line.delivered or date.today() > line.delivered + RETURN_WINDOW:
        return _error("OUTSIDE_WINDOW", "This item is outside the 90-day return window.",
                      "Explain the policy; offer a person if the customer disputes it.")
    refund = round(line.price * quantity, 2)
    status = "approved" if refund <= AUTO_REFUND_LIMIT else "pending_review"
    result = returns_store.create(customer, order_number, line_id, quantity,
                                  reason, refund, status, key=idempotency_key)
    return result


if __name__ == "__main__":
    server.run(transport="streamable-http")
