import numpy as np
from gen_sat_data import simulate_sat, FRONTDOOR_SEED


def descriptive_stats_table(data):
    """Markdown table comparing prep vs. no-prep students."""
    prep = data["prep_course"]
    sat = data["sat_score"]
    inc = data["family_income"]
    gpa = data["prior_gpa"]
    hours = data["hours_studied"]
    female = data["female"]

    t = prep == 1
    c = prep == 0

    rows = [
        ("Students", f"{c.sum():,}", f"{t.sum():,}", f"{len(prep):,}"),
        ("Female (%)", f"{female[c].mean():.0%}", f"{female[t].mean():.0%}",
         f"{female.mean():.0%}"),
        ("SAT Score", f"{sat[c].mean():,.0f}", f"{sat[t].mean():,.0f}",
         f"{sat.mean():,.0f}"),
        ("Family Income (k)", f"{inc[c].mean():.0f}k", f"{inc[t].mean():.0f}k",
         f"{inc.mean():.0f}k"),
        ("Hours Studied", f"{hours[c].mean():.1f}", f"{hours[t].mean():.1f}",
         f"{hours.mean():.1f}"),
        ("GPA", f"{gpa[c].mean():.2f}", f"{gpa[t].mean():.2f}",
         f"{gpa.mean():.2f}"),
    ]

    lines = [
        "| | No Prep | Prep | Overall |",
        "|:---|---:|---:|---:|",
    ]
    for label, no_p, p, overall in rows:
        lines.append(f"| {label} | {no_p} | {p} | {overall} |")

    return "\n".join(lines)


def adjustment_table(data):
    """Markdown table showing within-stratum effects by income tercile."""
    prep = data["prep_course"]
    sat = data["sat_score"]
    inc = data["family_income"]

    t = prep == 1
    c = prep == 0
    n = len(prep)

    terciles = np.percentile(inc, [33.3, 66.7])
    groups = np.digitize(inc, terciles)
    labels = [
        f"Low (< ${terciles[0]:.0f}k)",
        f"Middle (${terciles[0]:.0f}k–${terciles[1]:.0f}k)",
        f"High (> ${terciles[1]:.0f}k)",
    ]

    lines = [
        "| Income Group | Share of Population | SAT Diff (Prep − No Prep) | Weighted |",
        "|:---|---:|---:|---:|",
    ]

    adjusted = 0.0
    for g, lab in enumerate(labels):
        mask = groups == g
        share = mask.sum() / n
        t_mask = mask & t
        c_mask = mask & c
        diff = sat[t_mask].mean() - sat[c_mask].mean()
        weighted = share * diff
        adjusted += weighted
        lines.append(f"| {lab} | {share:.1%} | +{diff:.0f} pts | {weighted:.0f} |")

    lines.append(f"| **Adjusted estimate** | | | **+{adjusted:.0f} pts** |")

    return "\n".join(lines), adjusted


def frontdoor_numbers(data):
    """Compute front-door estimate from data where the criterion holds."""
    prep = data["prep_course"]
    hours = data["hours_studied"]
    sat = data["sat_score"]

    t = prep == 1
    c = prep == 0

    naive = sat[t].mean() - sat[c].mean()

    # Step 1: E[Hours | Prep=1] - E[Hours | Prep=0]
    dh = hours[t].mean() - hours[c].mean()

    # Step 2: within-group slopes of Hours -> SAT
    slopes = {}
    for pval, label in [(0, "No Prep"), (1, "Prep")]:
        mask = prep == pval
        coeffs = np.polyfit(hours[mask], sat[mask], 1)
        slopes[label] = coeffs[0]

    avg_slope = np.mean(list(slopes.values()))
    fd_estimate = dh * avg_slope

    return {
        "naive": naive,
        "hours_added": dh,
        "slope_no_prep": slopes["No Prep"],
        "slope_prep": slopes["Prep"],
        "avg_slope": avg_slope,
        "fd_estimate": fd_estimate,
    }


def main():
    """
    Generate markdown tables and inline numbers for the do-calculus blog post.

    Produces:
    1. Descriptive stats table (prep vs. no-prep)
    2. Backdoor adjustment table (income strata)
    3. Front-door estimation numbers

    Run:
        uv run python scripts/do-calculus/gen_tables.py
    """

    data = simulate_sat()
    prep = data["prep_course"]
    sat = data["sat_score"]
    t = prep == 1
    c = prep == 0
    naive = sat[t].mean() - sat[c].mean()

    print("=" * 60)
    print("DESCRIPTIVE STATS TABLE")
    print("=" * 60)
    print()
    print(descriptive_stats_table(data))
    print()
    print(f"Naive difference: {naive:.0f} pts")

    print()
    print("=" * 60)
    print("BACKDOOR ADJUSTMENT TABLE (income terciles)")
    print("=" * 60)
    print()
    table, adj = adjustment_table(data)
    print(table)
    print()
    print(f"Naive: {naive:.0f} pts -> Income-adjusted: {adj:.0f} pts")
    print("(Income alone doesn't block all backdoor paths)")

    # --- Front-door DGP ---
    fd_data = simulate_sat(frontdoor=True, seed=FRONTDOOR_SEED)
    fd = frontdoor_numbers(fd_data)

    print()
    print("=" * 60)
    print("FRONT-DOOR ESTIMATION (corrected DGP)")
    print("=" * 60)
    print()
    print(f"Naive difference: {fd['naive']:.0f} pts")
    print(f"Step 1: Prep adds {fd['hours_added']:.0f} hours of study")
    print(f"Step 2: Within No Prep group, slope = {fd['slope_no_prep']:.1f} pts/hr")
    print(f"        Within Prep group, slope = {fd['slope_prep']:.1f} pts/hr")
    print(f"        Average slope = {fd['avg_slope']:.1f} pts/hr")
    print(f"Front-door estimate: {fd['hours_added']:.0f} hrs × "
          f"{fd['avg_slope']:.1f} pts/hr ≈ {fd['fd_estimate']:.0f} pts")
    print("True ATE: ~55 pts (11 hrs × 5 pts/hr)")


if __name__ == "__main__":
    main()
