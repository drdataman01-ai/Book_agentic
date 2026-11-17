"""Simplified EU261 cancellation compensation (Chapter 9). Not legal advice:
the real rules have more conditions and are interpreted by courts."""

def eu261_cancellation(distance_km: float, intra_eu: bool, cause: str,
                       notice_days: int, reroute_delay_h: float) -> int:
    """Compensation in euros per passenger for a cancellation."""
    if cause in {"weather", "atc"}:             # extraordinary circumstances
        return 0
    if notice_days >= 14:
        return 0
    if distance_km <= 1500:
        amount, cutoff = 250, 2
    elif distance_km <= 3500 or intra_eu:
        amount, cutoff = 400, 3
    else:
        amount, cutoff = 600, 4
    if reroute_delay_h <= cutoff:               # rerouted close to the original time
        amount //= 2
    return amount

if __name__ == "__main__":
    for args in [(900, True, "technical", 0, 5.0), (900, True, "weather", 0, 5.0),
                 (2800, True, "crew", 2, 2.5), (5200, False, "technical", 0, 3.0)]:
        print(args, "->", eu261_cancellation(*args), "EUR")
