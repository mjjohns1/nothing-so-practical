import graphviz  # type: ignore[missing imports]
from pathlib import Path

OUT_DIR: Path = (
    Path(__file__).parent.parent.parent / "static/img/posts/do-calculus"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Colors
BACKDOOR_CLR = "#7A2A35"
CAUSAL_CLR = "#2C4A7A"
CUT_CLR = "#C0C0C0"
NODE_FACE = "#ECEEF2"
NODE_EDGE = "#6B7D92"
TEXT_CLR = "#1C2B3A"
INTERVENED_FACE = "#D6E4F0"
UNOBS_FACE = "#F5E6E6"

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

CUT_EDGE = {
    "color": CUT_CLR,
    "penwidth": "1.3",
    "arrowsize": "0.8",
    "style": "dashed",
}


def _save(g, name):
    out = OUT_DIR / name
    g.render(outfile=str(out), cleanup=True)
    print(f"Saved -> {out}")


# Dagitty positions (x right, y down) → graphviz neato (x right, y up).
# Negate y, then scale up for readable spacing.
SCALE = 2.0
DAGITTY_POS = {
    "parents_ed": (-0.394, -0.780),
    "income":     (-1.233, -0.540),
    "school":     (0.575,  -0.540),
    "motivation": (-0.394, -0.280),
    "gpa":        (-0.394,  0.061),
    "prep":       (-1.245,  0.469),
    "sat":        (0.575,   0.480),
}


def _pos(key):
    """Convert Dagitty pos to graphviz neato pos string with pin."""
    x, y = DAGITTY_POS[key]
    return f"{x * SCALE:.2f},{-y * SCALE:.2f}!"


def _make_sat_dag(mutilated=False):
    g = graphviz.Digraph(format="svg", engine="neato")
    g.attr(
        bgcolor="transparent",
        margin="0.3",
        overlap="false",
        splines="true",
    )
    g.node_attr.update(NODE_ATTRS)

    # Nodes at pinned positions
    g.node("parents_ed", "Parents\nEducation", pos=_pos("parents_ed"))
    g.node("income", "Family\nIncome", pos=_pos("income"))
    g.node("school", "School\nQuality", pos=_pos("school"))
    g.node("motivation", "Motivation", pos=_pos("motivation"))
    g.node("gpa", "GPA", pos=_pos("gpa"))

    prep_kw = {}
    if mutilated:
        prep_kw = {"fillcolor": INTERVENED_FACE, "color": CAUSAL_CLR}
    g.node("prep", "SAT Prep\nCourse", pos=_pos("prep"), **prep_kw)
    g.node("sat", "SAT\nScore", pos=_pos("sat"))

    # --- Edges ---

    # Arrows into Prep — severed in mutilated version
    arrow_into_prep = CUT_EDGE if mutilated else CONF_EDGE
    g.edge("income", "prep", **arrow_into_prep)
    g.edge("motivation", "prep", **arrow_into_prep)
    g.edge("gpa", "prep", **arrow_into_prep)

    # Confounding edges (always active)
    g.edge("parents_ed", "income", **CONF_EDGE)
    g.edge("parents_ed", "motivation", **CONF_EDGE)
    g.edge("income", "school", **CONF_EDGE)
    g.edge("school", "sat", **CONF_EDGE)
    g.edge("school", "gpa", **CONF_EDGE)
    g.edge("school", "motivation", **CONF_EDGE)
    g.edge("motivation", "sat", **CONF_EDGE)
    g.edge("motivation", "gpa", **CONF_EDGE)
    g.edge("gpa", "sat", **CONF_EDGE)

    # Causal edge
    g.edge("prep", "sat", **CAUSAL_EDGE)

    return g


def dag_full():
    _save(_make_sat_dag(mutilated=False), "sat-dag.svg")


def dag_obs():
    _save(_make_sat_dag(mutilated=False), "sat-dag-obs.svg")


def dag_do():
    _save(_make_sat_dag(mutilated=True), "sat-dag-do.svg")


def dag_frontdoor():
    g = graphviz.Digraph("frontdoor", format="svg", engine="neato")
    g.attr(
        bgcolor="transparent",
        margin="0.3",
        overlap="false",
        splines="true",
    )
    g.node_attr.update(NODE_ATTRS)

    # Unobserved confounder centered above prep and sat
    S = 2.0
    g.node("U", "Motivation\n(unobserved)",
           pos=f"0,{0.6 * S}!",
           fillcolor=UNOBS_FACE, color=BACKDOOR_CLR,
           style="rounded,filled,dashed")

    # Causal chain: all on the same bottom row
    g.node("prep", "SAT Prep\nCourse", pos=f"{-0.8 * S},0!")
    g.node("hours", "Hours\nStudied", pos="0,0!")
    g.node("sat", "SAT\nScore", pos=f"{0.8 * S},0!")

    # Confounding (dashed red)
    g.edge("U", "prep",
           color=BACKDOOR_CLR, style="dashed",
           penwidth="1.3", arrowsize="0.8")
    g.edge("U", "sat",
           color=BACKDOOR_CLR, style="dashed",
           penwidth="1.3", arrowsize="0.8")

    # Causal path (solid blue)
    g.edge("prep", "hours",
           color=CAUSAL_CLR, penwidth="1.5", arrowsize="0.8")
    g.edge("hours", "sat",
           color=CAUSAL_CLR, penwidth="1.5", arrowsize="0.8")

    _save(g, "frontdoor-dag.svg")


if __name__ == "__main__":
    dag_full()
    dag_obs()
    dag_do()
    dag_frontdoor()
