"""
DAG visualizations for the causal inference post.
Outputs:
  static/img/posts/causal-inference/dag-simple.svg
  static/img/posts/causal-inference/dag-income.svg
Run from repo root: python scripts/causal-inference/gen_dags.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent.parent / "static/img/posts/causal-inference"

# --- Palette -------------------------------------------------------------
NODE_FACE    = "#ECEEF2"
NODE_EDGE    = "#6B7D92"
TEXT_CLR     = "#1C2B3A"
BACKDOOR_CLR = "#7A2A35"
CAUSAL_CLR   = "#2C4A7A"

plt.rcParams.update({
    "font.family":      "sans-serif",
    "figure.facecolor": "none",
    "axes.facecolor":   "none",
})

NODE_W      = 0.21
NODE_H      = 0.18
NODE_H_TALL = 0.22   # Z node has 3 lines

# --- Helpers -------------------------------------------------------------

def box_edge(center, direction, w, h, pad=0.028):
    """Return the point on (or just outside) the node box boundary."""
    cx, cy = center
    dx, dy = direction
    hw = w / 2 + pad
    hh = h / 2 + pad
    tx = (hw / abs(dx)) if abs(dx) > 1e-9 else float("inf")
    ty = (hh / abs(dy)) if abs(dy) > 1e-9 else float("inf")
    t = min(tx, ty)
    return (cx + dx * t, cy + dy * t)


def add_node(ax, pos, lines, w=NODE_W, h=NODE_H):
    x, y = pos
    patch = mpatches.FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.018",
        fc=NODE_FACE, ec=NODE_EDGE, lw=1.3, zorder=2,
    )
    ax.add_patch(patch)
    ax.text(x, y, "\n".join(lines), ha="center", va="center",
            fontsize=10, color=TEXT_CLR, zorder=4, linespacing=1.5)


def add_arrow(ax, src, dst, src_wh, dst_wh, color,
              label="", rad=0.0, dashed=False, pad=0.028):
    """
    src / dst      : node center (data coords)
    src_wh/dst_wh  : (w, h) of source/dest node
    """
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    length = np.hypot(dx, dy)
    ux, uy = dx / length, dy / length

    if rad == 0.0:
        # Exact edge points → no shrink needed
        p_src = box_edge(src, ( ux,  uy), *src_wh, pad=pad)
        p_dst = box_edge(dst, (-ux, -uy), *dst_wh, pad=pad)
        shrinkA = shrinkB = 0
    else:
        # Curved arrow: use the node centre and let shrink handle it.
        # Compute shrink from the box half-extents in pts at 72dpi/5.8" figure.
        # (Income→Y is the only curved arrow; it hits Y from the top-right.)
        p_src, p_dst = src, dst
        # shrink ~ distance to node edge along straight chord
        def pts_shrink(center, approach_dir, wh):
            hw, hh = wh[0] / 2, wh[1] / 2
            adx, ady = abs(approach_dir[0]), abs(approach_dir[1])
            tx = (hw / adx) if adx > 1e-9 else float("inf")
            ty = (hh / ady) if ady > 1e-9 else float("inf")
            edge_frac = min(tx, ty)   # data units to edge
            return edge_frac * 5.8 * 72 + 4   # convert to points + padding
        shrinkA = pts_shrink(src, ( ux,  uy), src_wh)
        shrinkB = pts_shrink(dst, (-ux, -uy), dst_wh)

    ls = (0, (5, 3)) if dashed else "solid"
    patch = FancyArrowPatch(
        posA=p_src, posB=p_dst,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>",
        mutation_scale=22,
        color=color, lw=1.5,
        linestyle=ls,
        shrinkA=shrinkA, shrinkB=shrinkB,
        zorder=3,
    )
    ax.add_patch(patch)

    if label:
        mx = (src[0] + dst[0]) / 2
        my = (src[1] + dst[1]) / 2
        nx, ny = -uy, ux   # left-hand normal
        ax.text(mx + nx * 0.05, my + ny * 0.05, label,
                ha="center", va="center",
                fontsize=11, color=color,
                style="italic", fontweight="semibold", zorder=5)


# --- Legend --------------------------------------------------------------

def add_legend(ax):
    handles = [
        Line2D([0], [0], color=BACKDOOR_CLR, lw=1.5,
               label="Confounding path"),
        Line2D([0], [0], color=CAUSAL_CLR,   lw=1.5,
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


# --- Shared node positions -----------------------------------------------
Z_POS = (0.50, 0.64)
X_POS = (0.16, 0.18)
Y_POS = (0.84, 0.18)

WH_STD  = (NODE_W, NODE_H)
WH_TALL = (NODE_W, NODE_H_TALL)


# --- DAG 1: simple confounding -------------------------------------------

def dag_simple():
    fig, ax = plt.subplots(figsize=(5.8, 3.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.12, 1)
    ax.axis("off")

    add_arrow(ax, Z_POS, X_POS, WH_TALL, WH_STD,  BACKDOOR_CLR)
    add_arrow(ax, Z_POS, Y_POS, WH_TALL, WH_STD,  BACKDOOR_CLR)
    add_arrow(ax, X_POS, Y_POS, WH_STD,  WH_STD,  CAUSAL_CLR, label="?", dashed=True)

    add_node(ax, Z_POS, ["Health", "Consciousness", "(Z)"], h=NODE_H_TALL)
    add_node(ax, X_POS, ["HRT", "(X)"])
    add_node(ax, Y_POS, ["Heart Disease", "(Y)"])

    add_legend(ax)

    plt.tight_layout()
    out = OUT_DIR / "dag-simple.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close(fig)


# --- DAG 2: with income --------------------------------------------------

def dag_income():
    fig, ax = plt.subplots(figsize=(5.8, 4.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.12, 1)
    ax.axis("off")

    scale = 0.78
    def s(pos):
        return (pos[0], pos[1] * scale)

    Z = s(Z_POS)
    X = s(X_POS)
    Y = s(Y_POS)
    INC = (0.50, 0.88)

    PAD = 0.018
    add_arrow(ax, INC,  Z,    WH_STD,  WH_TALL, BACKDOOR_CLR, pad=PAD)
    add_arrow(ax, INC,  Y,    WH_STD,  WH_STD,  BACKDOOR_CLR, rad=-0.15, pad=PAD)
    add_arrow(ax, Z,    X,    WH_TALL, WH_STD,  BACKDOOR_CLR, pad=PAD)
    add_arrow(ax, Z,    Y,    WH_TALL, WH_STD,  BACKDOOR_CLR, pad=PAD)
    add_arrow(ax, X,    Y,    WH_STD,  WH_STD,  CAUSAL_CLR, label="?", dashed=True, pad=PAD)

    add_node(ax, INC, ["Income"])
    add_node(ax, Z,   ["Health", "Consciousness", "(Z)"], h=NODE_H_TALL)
    add_node(ax, X,   ["HRT", "(X)"])
    add_node(ax, Y,   ["Heart Disease", "(Y)"])

    add_legend(ax)

    plt.tight_layout()
    out = OUT_DIR / "dag-income.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close(fig)


if __name__ == "__main__":
    dag_simple()
    dag_income()
