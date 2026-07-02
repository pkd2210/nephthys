from __future__ import annotations

from math import cos
from math import pi
from math import sin
from xml.sax.saxutils import escape


def _polar_to_cartesian(
    cx: float, cy: float, radius: float, angle_deg: float
) -> tuple[float, float]:
    angle_rad = (angle_deg - 90.0) * pi / 180.0
    return (cx + radius * cos(angle_rad), cy + radius * sin(angle_rad))


def _describe_slice(
    cx: float,
    cy: float,
    radius: float,
    start_angle: float,
    end_angle: float,
) -> str:
    start_x, start_y = _polar_to_cartesian(cx, cy, radius, end_angle)
    end_x, end_y = _polar_to_cartesian(cx, cy, radius, start_angle)
    large_arc = 1 if end_angle - start_angle > 180 else 0
    return (
        f"M {cx:.2f} {cy:.2f} "
        f"L {end_x:.2f} {end_y:.2f} "
        f"A {radius:.2f} {radius:.2f} 0 {large_arc} 1 {start_x:.2f} {start_y:.2f} Z"
    )


def generate_pie_chart(
    y: list[int], labels: list[str], colours: list[str], text_colour: str, bg_colour: str
) -> bytes:
    total = sum(y)
    width = 640
    height = 360
    cx = 170.0
    cy = 185.0
    radius = 110.0

    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ),
        f'<rect width="100%" height="100%" fill="{escape(bg_colour)}" />',
        f'<text x="32" y="46" fill="{escape(text_colour)}" font-size="24" font-weight="700">Ticket status</text>',
    ]

    if total <= 0:
        svg_parts.extend(
            [
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#d1d5db" opacity="0.9" />',
                f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" fill="{escape(text_colour)}" font-size="18" font-weight="700">No tickets</text>',
                f'<text x="{cx}" y="{cy + 18}" text-anchor="middle" fill="{escape(text_colour)}" font-size="12">in the last 7 days</text>',
            ]
        )
    else:
        start_angle = -90.0
        for label, count, colour in zip(labels, y, colours, strict=False):
            if count <= 0:
                continue
            sweep = (count / total) * 360.0
            end_angle = start_angle + sweep
            path = _describe_slice(cx, cy, radius, start_angle, end_angle)
            percent = (count / total) * 100.0
            mid_angle = start_angle + sweep / 2.0
            text_x, text_y = _polar_to_cartesian(cx, cy, radius * 0.62, mid_angle)
            svg_parts.extend(
                [
                    f'<path d="{path}" fill="{escape(colour)}" stroke="{escape(bg_colour)}" stroke-width="2" />',
                    f'<text x="{text_x:.2f}" y="{text_y:.2f}" text-anchor="middle" dominant-baseline="middle" fill="#111827" font-size="12" font-weight="700">{percent:.1f}%</text>',
                ]
            )
            start_angle = end_angle

    legend_x = 345
    legend_y = 108
    legend_gap = 42
    visible_rows = 0
    for label, count, colour in zip(labels, y, colours, strict=False):
        if count <= 0:
            continue
        percent = (count / total * 100.0) if total > 0 else 0.0
        row_y = legend_y + visible_rows * legend_gap
        svg_parts.extend(
            [
                f'<rect x="{legend_x}" y="{row_y - 14}" width="16" height="16" rx="4" fill="{escape(colour)}" />',
                f'<text x="{legend_x + 26}" y="{row_y}" fill="{escape(text_colour)}" font-size="16" font-weight="600">{escape(label)}</text>',
                f'<text x="{legend_x + 26}" y="{row_y + 18}" fill="{escape(text_colour)}" font-size="12">{count} tickets ({percent:.1f}%)</text>',
            ]
        )
        visible_rows += 1

    if visible_rows == 0:
        svg_parts.append(
            f'<text x="{legend_x}" y="{legend_y}" fill="{escape(text_colour)}" font-size="16">No active statuses</text>'
        )

    svg_parts.append("</svg>")
    return "".join(svg_parts).encode("utf-8")
