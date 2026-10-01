from enum import Enum
from typing import Optional


class GeofenceState(str, Enum):
    UNKNOWN = "UNKNOWN"
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


class GeofenceEventType(str, Enum):
    ENTER = "ENTER"
    EXIT = "EXIT"
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


def determine_transition(
    previous_state: str,
    current_state: str,
    record_periodic_inside: bool = True,
    record_periodic_outside: bool = False,
) -> Optional[str]:
    """
    Given previous_state ('UNKNOWN', 'INSIDE', 'OUTSIDE') and current_state ('INSIDE', 'OUTSIDE'),
    determine the event type ('ENTER', 'EXIT', 'INSIDE', 'OUTSIDE', or None if suppressed).

    State Machine Transitions:
    - UNKNOWN -> INSIDE  : ENTER
    - UNKNOWN -> OUTSIDE : OUTSIDE (Initial state registration)
    - OUTSIDE -> INSIDE  : ENTER
    - INSIDE  -> OUTSIDE : EXIT
    - INSIDE  -> INSIDE  : INSIDE (if record_periodic_inside is True) else None
    - OUTSIDE -> OUTSIDE : OUTSIDE (if record_periodic_outside is True) else None
    """
    prev = previous_state.upper() if previous_state else "UNKNOWN"
    curr = current_state.upper()

    if curr == "INSIDE":
        if prev in ("OUTSIDE", "UNKNOWN"):
            return GeofenceEventType.ENTER.value
        elif prev == "INSIDE":
            return GeofenceEventType.INSIDE.value if record_periodic_inside else None
    elif curr == "OUTSIDE":
        if prev == "UNKNOWN":
            # Initial state registration for outside
            return GeofenceEventType.OUTSIDE.value
        elif prev == "INSIDE":
            return GeofenceEventType.EXIT.value
        elif prev == "OUTSIDE":
            return GeofenceEventType.OUTSIDE.value if record_periodic_outside else None

    return None
