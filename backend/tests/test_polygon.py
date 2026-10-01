from app.geofencing.polygon import is_inside_polygon, ray_casting_point_in_polygon

# Triangle polygon: (0,0), (0,10), (10,0)
TRIANGLE = [(0.0, 0.0), (0.0, 10.0), (10.0, 0.0)]

# Square: (10, 10) to (20, 20)
SQUARE = [(10.0, 10.0), (10.0, 20.0), (20.0, 20.0), (20.0, 10.0)]

# Concave / L-shaped polygon:
# (0,0) -> (0,4) -> (2,4) -> (2,2) -> (4,2) -> (4,0)
CONCAVE_L = [
    (0.0, 0.0),
    (0.0, 4.0),
    (2.0, 4.0),
    (2.0, 2.0),
    (4.0, 2.0),
    (4.0, 0.0),
]


def test_polygon_triangle_inside():
    assert is_inside_polygon(2.0, 2.0, TRIANGLE) is True


def test_polygon_triangle_outside():
    assert is_inside_polygon(8.0, 8.0, TRIANGLE) is False


def test_polygon_square_inside():
    assert is_inside_polygon(15.0, 15.0, SQUARE) is True


def test_polygon_square_outside():
    assert is_inside_polygon(5.0, 5.0, SQUARE) is False
    assert is_inside_polygon(25.0, 25.0, SQUARE) is False


def test_concave_polygon():
    # Point (1, 3) is inside the upper branch of the L
    assert is_inside_polygon(1.0, 3.0, CONCAVE_L) is True
    # Point (3, 1) is inside the right branch of the L
    assert is_inside_polygon(3.0, 1.0, CONCAVE_L) is True
    # Point (3, 3) is in the cut-out corner (outside)
    assert is_inside_polygon(3.0, 3.0, CONCAVE_L) is False


def test_invalid_polygon_points():
    # Less than 3 points
    assert is_inside_polygon(1.0, 1.0, [(0.0, 0.0), (1.0, 1.0)]) is False


def test_ray_casting_fallback():
    assert ray_casting_point_in_polygon(15.0, 15.0, SQUARE) is True
    assert ray_casting_point_in_polygon(5.0, 5.0, SQUARE) is False
