"""The disruption case that every agent reads and updates (Chapter 9)."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

Stage = Literal["intake", "rebooking", "care", "human", "closed"]

class SeatHold(BaseModel):
    flight: str
    cabin: Literal["economy", "premium", "business"]
    hold_id: str
    expires_at: datetime

class DisruptionCase(BaseModel):
    case_id: str
    booking_ref: str                        # verified at intake, never from free text
    passengers: list[str] = Field(min_length=1)
    original_flight: str
    cause: Literal["weather", "technical", "crew", "atc", "other"]
    stage: Stage = "intake"
    owner: str = "intake_agent"             # exactly one owner at a time
    needs: list[str] = []                   # e.g. "wheelchair", "travelling with infant"
    hold: SeatHold | None = None
    new_itinerary: list[str] = []
    compensation_eur: int | None = None     # computed by rules, never by a model
    history: list[str] = []

ALLOWED = {("intake", "rebooking"), ("rebooking", "care"), ("care", "closed"),
           ("intake", "human"), ("rebooking", "human"), ("care", "human")}

def hand_off(case: DisruptionCase, to_stage: Stage, to_owner: str, note: str) -> DisruptionCase:
    """Move ownership of the case. Refuses transitions the design does not allow."""
    if (case.stage, to_stage) not in ALLOWED:
        raise ValueError(f"Handoff {case.stage} -> {to_stage} is not allowed.")
    if to_stage == "care" and not case.new_itinerary:
        raise ValueError("Cannot move to care before a new itinerary is confirmed.")
    return case.model_copy(update={
        "stage": to_stage, "owner": to_owner,
        "history": case.history + [f"{case.owner} -> {to_owner}: {note}"]})
