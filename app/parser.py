from __future__ import annotations

import re
from typing import Iterable, List

_BRACKET_REGEX = re.compile(r"\[\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\]")
_PAREN_REGEX = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")
_KEYED_REGEX = re.compile(
    r"x0\s*=\s*(-?\d+)\D+y0\s*=\s*(-?\d+)\D+x1\s*=\s*(-?\d+)\D+y1\s*=\s*(-?\d+)",
    re.IGNORECASE,
)
_INT_REGEX = re.compile(r"(?<![A-Za-z])-?\d+")


def parse_bbox(raw_text: str) -> List[int]:
    for regex in (_BRACKET_REGEX, _PAREN_REGEX, _KEYED_REGEX):
        m = regex.search(raw_text)
        if m:
            return [int(m.group(i)) for i in range(1, 5)]

    nums = [int(v) for v in _INT_REGEX.findall(raw_text)]
    if len(nums) < 4:
        return [-1, -1, -1, -1]
    return nums[:4]


def clamp_bbox(bbox: Iterable[int], width: int, height: int) -> List[int]:
    x0, y0, x1, y1 = [int(v) for v in bbox]
    if x0 < 0 or y0 < 0 or x1 < 0 or y1 < 0:
        return [-1, -1, -1, -1]

    x0 = max(0, min(x0, width - 1))
    x1 = max(0, min(x1, width - 1))
    y0 = max(0, min(y0, height - 1))
    y1 = max(0, min(y1, height - 1))

    if x1 <= x0 or y1 <= y0:
        return [-1, -1, -1, -1]
    return [x0, y0, x1, y1]
