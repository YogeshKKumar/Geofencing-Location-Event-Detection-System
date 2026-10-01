from app.geofencing.state import determine_transition, GeofenceEventType, GeofenceState


def test_transition_unknown_to_inside():
    ev = determine_transition("UNKNOWN", "INSIDE")
    assert ev == GeofenceEventType.ENTER.value


def test_transition_unknown_to_outside():
    ev = determine_transition("UNKNOWN", "OUTSIDE")
    assert ev == GeofenceEventType.OUTSIDE.value


def test_transition_outside_to_inside():
    ev = determine_transition("OUTSIDE", "INSIDE")
    assert ev == GeofenceEventType.ENTER.value


def test_transition_inside_to_outside():
    ev = determine_transition("INSIDE", "OUTSIDE")
    assert ev == GeofenceEventType.EXIT.value


def test_transition_inside_to_inside():
    # With record_periodic_inside=True
    ev_periodic = determine_transition("INSIDE", "INSIDE", record_periodic_inside=True)
    assert ev_periodic == GeofenceEventType.INSIDE.value

    # With record_periodic_inside=False
    ev_none = determine_transition("INSIDE", "INSIDE", record_periodic_inside=False)
    assert ev_none is None


def test_transition_outside_to_outside():
    # By default, periodic outside is disabled
    ev = determine_transition("OUTSIDE", "OUTSIDE", record_periodic_outside=False)
    assert ev is None

    # When enabled
    ev_periodic = determine_transition("OUTSIDE", "OUTSIDE", record_periodic_outside=True)
    assert ev_periodic == GeofenceEventType.OUTSIDE.value


def test_no_duplicate_enter_when_already_inside():
    # If device was INSIDE, receiving another location inside should NEVER generate ENTER
    ev = determine_transition("INSIDE", "INSIDE", record_periodic_inside=False)
    assert ev != GeofenceEventType.ENTER.value


def test_no_duplicate_exit_when_already_outside():
    # If device was OUTSIDE, receiving another location outside should NEVER generate EXIT
    ev = determine_transition("OUTSIDE", "OUTSIDE")
    assert ev != GeofenceEventType.EXIT.value
