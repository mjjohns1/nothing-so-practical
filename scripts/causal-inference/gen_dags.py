import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from pathlib import Path

OUT_DIR: Path = (
    Path(__file__).parent.parent.parent / "static/img/posts/causal-inference"
)

NODE_FACE: str = "#ECEEF2"
NODE_EDGE: str = "#6B7D92"
TEXT_CLR: str = "#1C2B3A"
BACKDOOR_CLR: str = "#7A2A35"
CAUSAL_CLR: str = "#2C4A7A"

plt.rcParams.update({
    "font.family": "sans-serif",
    "figure.facecolor": "none",
    "axes.facecolor":   "none",
})

Coord = tuple[float, float]
WH = tuple[float, float]

NODE_W: float = 0.21
NODE_H: float = 0.18
NODE_H_TALL: float = 0.22  # Z node has 3 lines


def box_edge(
    center: Coord,
    direction: Coord,
    w: float,
    h: float,
    pad: float = 0.028
) -> Coord:

    """Return the point on (or just outside) the node box boundary."""

    cx, cy = center
    dx, dy = direction
    hw: float = w / 2 + pad
    hh: float = h / 2 + pad
    tx: float = (hw / abs(dx)) if abs(dx) > 1e-9 else float("inf")
    ty: float = (hh / abs(dy)) if abs(dy) > 1e-9 else float("inf")
    t: float = min(tx, ty)

    return (cx + dx * t, cy + dy * t)


def add_node(
    ax: Axes,
    pos: Coord,
    lines: list[str],
    w: float = NODE_W,
    h: float = NODE_H
) -> None:
    x, y = pos
    patch: mpatches.FancyBboxPatch = mpatches.FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.018",
        fc=NODE_FACE, ec=NODE_EDGE, lw=1.3, zorder=2,
    )
    ax.add_patch(patch)
    ax.text(x, y, "\n".join(lines), ha="center", va="center",
            fontsize=10, color=TEXT_CLR, zorder=4, linespacing=1.5)


def _edge_shrink_pts(approach_dir: Coord, wh: WH) -> float:
    """Shrink distance in points for curved FancyArrowPatch edges."""

    hw: float = wh[0] / 2
    hh: float = wh[1] / 2
    adx: float = abs(approach_dir[0])
    ady: float = abs(approach_dir[1])
    tx: float = (hw / adx) if adx > 1e-9 else float("inf")
    ty: float = (hh / ady) if ady > 1e-9 else float("inf")
    edge_frac: float = min(tx, ty)  # data units to edge

    return edge_frac * 5.8 * 72 + 4  # convert to points + padding


def add_arrow(
    ax: Axes,
    src: Coord,
    dst: Coord,
    src_wh: WH,
    dst_wh: WH,
    color: str,
    label: str = "",
    rad: float = 0.0,
    dashed: bool = False,
    pad: float = 0.028
) -> None:
    """
    src / dst      : node center (data coords)
    src_wh/dst_wh  : (w, h) of source/dest node
    """

    dx: float = dst[0] - src[0]
    dy: float = dst[1] - src[1]
    length: float = np.hypot(dx, dy)
    ux: float = dx / length
    uy: float = dy / length

    if rad == 0.0:
        # Exact edge points - no shrink needed
        p_src: Coord = box_edge(src, (ux, uy), *src_wh, pad=pad)
        p_dst: Coord = box_edge(dst, (-ux, -uy), *dst_wh, pad=pad)
        shrink_a: float = 0
        shrink_b: float = 0
    else:
        # Curved arrow: use the node centre and let shrink handle it.
        p_src, p_dst = src, dst
        shrink_a = _edge_shrink_pts((ux, uy), src_wh)
        shrink_b = _edge_shrink_pts((-ux, -uy), dst_wh)

    ls: str | tuple[int, tuple[int, int]] = (
        (0, (5, 3)) if dashed else "solid"
    )
    arrow: mpatches.FancyArrowPatch = mpatches.FancyArrowPatch(
        posA=p_src, posB=p_dst,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>",
        mutation_scale=22,
        color=color, lw=1.5,
        linestyle=ls,
        shrinkA=shrink_a, shrinkB=shrink_b,
        zorder=3,
    )
    ax.add_patch(arrow)

    if label:
        mx: float = (src[0] + dst[0]) / 2
        my: float = (src[1] + dst[1]) / 2
        nx: float = -uy
        ny: float = ux  # left-hand normal
        ax.text(mx + nx * 0.05, my + ny * 0.05, label,
                ha="center", va="center",
                fontsize=11, color=color,
                style="italic", fontweight="semibold", zorder=5)


def add_legend(ax: Axes) -> None:
    handles: list[Line2D] = [
        Line2D([0], [0], color=BACKDOOR_CLR, lw=1.5,
               label="Confounding path"),
        Line2D([0], [0], color=CAUSAL_CLR, lw=1.5,
               linestyle=(0, (5, 3)), label="Causal path"),
    ]
    ax.legend(
        handles=handles,
        loc="lower center",
        ncol=2,
        fontsize=9,
        handlelength=2.2,
        columnspacing=1.2,
        framealpha=0.9,
        edgecolor=NODE_EDGE,
        facecolor="white",
    )


# Shared node positions
Z_POS: Coord = (0.50, 0.64)
X_POS: Coord = (0.16, 0.18)
Y_POS: Coord = (0.84, 0.18)

WH_STD: WH = (NODE_W, NODE_H)
WH_TALL: WH = (NODE_W, NODE_H_TALL)


def dag_simple() -> None:
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.12, 0.82)
    ax.axis("off")

    add_arrow(ax, Z_POS, X_POS, WH_TALL, WH_STD, BACKDOOR_CLR)
    add_arrow(ax, Z_POS, Y_POS, WH_TALL, WH_STD, BACKDOOR_CLR)
    add_arrow(ax, X_POS, Y_POS, WH_STD, WH_STD,
              CAUSAL_CLR, dashed=True)

    add_node(ax, Z_POS, ["Health", "Consciousness", "(Z)"],
             h=NODE_H_TALL)
    add_node(ax, X_POS, ["HRT", "(X)"])
    add_node(ax, Y_POS, ["Heart Disease", "(Y)"])

    add_legend(ax)

    plt.tight_layout()
    out: Path = OUT_DIR / "dag-simple.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close(fig)


def dag_income() -> None:
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(5.8, 4.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.12, 1)
    ax.axis("off")

    scale: float = 0.78

    def scaled(pos: Coord) -> Coord:
        return (pos[0], pos[1] * scale)

    z_pos: Coord = scaled(Z_POS)
    x_pos: Coord = scaled(X_POS)
    y_pos: Coord = scaled(Y_POS)
    inc_pos: Coord = (0.50, 0.88)

    pad: float = 0.018
    add_arrow(ax, inc_pos, z_pos, WH_STD, WH_TALL,
              BACKDOOR_CLR, pad=pad)
    add_arrow(ax, inc_pos, y_pos, WH_STD, WH_STD,
              BACKDOOR_CLR, rad=-0.15, pad=pad)
    add_arrow(ax, z_pos, x_pos, WH_TALL, WH_STD,
              BACKDOOR_CLR, pad=pad)
    add_arrow(ax, z_pos, y_pos, WH_TALL, WH_STD,
              BACKDOOR_CLR, pad=pad)
    add_arrow(ax, x_pos, y_pos, WH_STD, WH_STD,
              CAUSAL_CLR, dashed=True, pad=pad)

    add_node(ax, inc_pos, ["Income"])
    add_node(ax, z_pos, ["Health", "Consciousness", "(Z)"],
             h=NODE_H_TALL)
    add_node(ax, x_pos, ["HRT", "(X)"])
    add_node(ax, y_pos, ["Heart Disease", "(Y)"])

    add_legend(ax)

    plt.tight_layout()
    out: Path = OUT_DIR / "dag-income.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close(fig)


if __name__ == "__main__":
    dag_simple()
    dag_income()
