from __future__ import annotations

import os

from napari_arboretum.tree import Annotation, Edge

SVG_HEADER = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
    '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
)

SVG_FOOTER = "</g>\n</svg>"


def svg_line_from_edge(edge: Edge, view_box: tuple) -> str:
    x1 = ((edge.y[0] - view_box[0]) / view_box[2]) * 100
    y1 = ((edge.x[1] - view_box[1]) / view_box[3]) * 100
    x2 = ((edge.y[1] - view_box[0]) / view_box[2]) * 100
    y2 = ((edge.x[0] - view_box[1]) / view_box[3]) * 100
    svg_line = (
        f'    <line x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%" '
        f'stroke="black" '
        f'stroke-width="1" '
    )

    if edge.node is None:
        svg_line += 'stroke-dasharray="1" '

    svg_line += "/> \n"
    return svg_line


def svg_text_from_annotation(annotation: Annotation, view_box: tuple) -> str:
    x1 = ((annotation.y - view_box[0]) / view_box[2]) * 100
    y1 = ((annotation.x - view_box[1]) / view_box[3]) * 100
    txt = annotation.label
    svg_text = f'<text text-anchor="start" x="{x1}%" y="{y1}%">{txt}</text>'
    return svg_text


def svg_view_box(*, width: int = 512, height: int = 512) -> str:
    svg_box = (
        f'<svg viewBox="0 0 {width} {height}" '
        'xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">'
    )
    return svg_box


def export_svg(
    filename: os.PathLike,
    edges: list[Edge],
    annotations: list[Annotation],
) -> None:
    """Export the tree as an SVG file."""
    min_x = min([e.y[0] for e in edges])
    min_y = min([e.x[0] for e in edges])
    width = max(max([e.y[1] for e in edges]) - min_x, 1)
    height = max(max([e.x[1] for e in edges]) - min_y, 1)

    view_box = (min_x, min_y, width, height)

    with open(filename, "w") as svg_file:
        svg_file.write(SVG_HEADER)
        svg_file.write(svg_view_box())
        svg_file.write("<g> \n")
        for edge in edges:
            svg_line = svg_line_from_edge(edge, view_box)
            svg_file.write(svg_line)
        for annotation in annotations:
            svg_text = svg_text_from_annotation(annotation, view_box)
            svg_file.write(svg_text)
        svg_file.write(SVG_FOOTER)
