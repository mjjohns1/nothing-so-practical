"""
Generate DAG visualizations for the causal inference blog posts.

Uses Graphviz neato engine with pinned positions for clean layout.

Produces:
  1. dag-simple.svg   Simple confounding: Z -> X, Y; X -> Y
  2. dag-income.svg   Multiple confounders: Income -> Z, X, Y; Z -> X, Y; X -> Y
"""

import graphviz
from pathlib import Path

OUT_DIR: Path = (
    Path(__file__).parent.parent.parent / "static/img/posts/causal-inference"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Colors (consistent with series)
NODE_FACE = "#ECEEF2"
NODE_EDGE = "#6B7D92"
TEXT_CLR = "#1C2B3A"
BACKDOOR_CLR = "#7A2A35"
CAUSAL_CLR = "#2C4A7A"

NODE_ATTRS = {
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": NODE_FACE,
    "color": NODE_EDGE,
    "fontname": "Helvetica",
    "fontsize": "12",
    "fontcolor": TEXT_CLR,
    "penwidth": "1.3",
    "width": "1.4",
    "height": "0.5",
}

CONF_EDGE = {
    "color": BACKDOOR_CLR,
    "penwidth": "1.3",
    "arrowsize": "0.8",
}

CAUSAL_EDGE = {
    "color": CAUSAL_CLR,
    "style": "dashed",
    "penwidth": "1.5",
    "arrowsize": "0.8",
}


def _save(g, name):
    out = OUT_DIR / name
    g.render(outfile=str(out), cleanup=True)
    print(f"Saved -> {out}")


def dag_simple():
    """Simple confounding DAG for HRT example.

    Layout:
              Health Consciousness (Z)
             /                        \\
            v                          v
        HRT (X)  - - - - - - ->  Heart Disease (Y)
    """
    g = graphviz.Digraph(format="svg", engine="neato")
    g.attr(bgcolor="transparent", margin="0.3",
           overlap="false", splines="true")
    g.node_attr.update(NODE_ATTRS)

    S = 2.0
    g.node("Z", "Health\nConsciousness\n(Z)", pos=f"0,{0.7 * S}!")
    g.node("X", "HRT\n(X)", pos=f"{-0.7 * S},0!")
    g.node("Y", "Heart Disease\n(Y)", pos=f"{0.7 * S},0!")

    g.edge("Z", "X", **CONF_EDGE)
    g.edge("Z", "Y", **CONF_EDGE)
    g.edge("X", "Y", **CAUSAL_EDGE)

    _save(g, "dag-simple.svg")


def dag_income():
    """Multiple confounders DAG for HRT example.

    Layout:
                    Income
                   /      \\
                  v        v
        Family Income    Health Consciousness (Z)
              |         /          |
              v        v           v
            HRT (X)  - - - ->  Heart Disease (Y)

    Simplified: Income at top, Z in middle, X and Y at bottom.
    """
    g = graphviz.Digraph(format="svg", engine="neato")
    g.attr(bgcolor="transparent", margin="0.3",
           overlap="false", splines="true")
    g.node_attr.update(NODE_ATTRS)

    S = 2.0
    g.node("Inc", "Income", pos=f"0,{0.9 * S}!")
    g.node("Z", "Health\nConsciousness\n(Z)", pos=f"0,{0.45 * S}!")
    g.node("X", "HRT\n(X)", pos=f"{-0.7 * S},0!")
    g.node("Y", "Heart Disease\n(Y)", pos=f"{0.7 * S},0!")

    # Income confounding
    g.edge("Inc", "Z", **CONF_EDGE)
    g.edge("Inc", "X", **CONF_EDGE)
    g.edge("Inc", "Y", **CONF_EDGE)

    # Z confounding
    g.edge("Z", "X", **CONF_EDGE)
    g.edge("Z", "Y", **CONF_EDGE)

    # Causal
    g.edge("X", "Y", **CAUSAL_EDGE)

    _save(g, "dag-income.svg")


if __name__ == "__main__":
    dag_simple()
    dag_income()
