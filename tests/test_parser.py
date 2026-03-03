from app.parser import clamp_bbox, parse_bbox


def test_parse_bbox_variants():
    assert parse_bbox("[12,34,56,78]") == [12, 34, 56, 78]
    assert parse_bbox("bbox: (12, 34, 56, 78)") == [12, 34, 56, 78]
    assert parse_bbox("x0=12 y0=34 x1=56 y1=78") == [12, 34, 56, 78]
    assert parse_bbox("not found") == [-1, -1, -1, -1]


def test_clamp_bbox():
    assert clamp_bbox([10, 20, 30, 40], 100, 200) == [10, 20, 30, 40]
    assert clamp_bbox([10, 20, 130, 240], 100, 200) == [10, 20, 99, 199]
    assert clamp_bbox([-1, 1, 10, 20], 100, 100) == [-1, -1, -1, -1]
    assert clamp_bbox([10, 10, 9, 20], 100, 100) == [-1, -1, -1, -1]
