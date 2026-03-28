"""
Simulate a fake SAT prep course observational dataset.

The data generating process matches the Dagitty DAG:
  Parents Education --> Family Income, Motivation
  Family Income     --> SAT Prep Course, School Quality
  School Quality    --> SAT Score, GPA, Motivation
  Motivation        --> SAT Prep Course, SAT Score, GPA
  GPA               --> SAT Prep Course, SAT Score
  SAT Prep Course   --> Hours Studied
  Hours Studied     --> SAT Score

True causal effect of Prep Course on SAT Score (via Hours Studied): ~40 pts.
"""

import numpy as np

SEED = 42


def simulate_sat(n=5000, seed=SEED):
    """Return a dict of arrays with the simulated SAT dataset."""

    rng = np.random.default_rng(seed)

    # Exogenous root
    parents_ed = rng.normal(0, 1, n)  # standardized

    # Parents Education -> Family Income, Motivation
    family_income = (
        75 + 20 * parents_ed + rng.normal(0, 15, n)
    ).clip(15, 200)  # $k

    inc_z = (family_income - 75) / 25  # standardized for coefficients

    # Family Income -> School Quality
    school_quality = 0.4 * inc_z + rng.normal(0, 0.6, n)

    # Parents Education + School Quality -> Motivation
    motivation = (
        0.35 * parents_ed
        + 0.25 * school_quality
        + rng.normal(0, 0.7, n)
    )

    # School Quality + Motivation -> GPA
    prior_gpa = (
        0.3 * school_quality
        + 0.35 * motivation
        + rng.normal(0, 0.5, n)
    )

    # Treatment assignment (self-selection)
    # Family Income, Motivation, GPA -> Prep Course
    prep_logit = (
        -0.8
        + 0.4 * inc_z
        + 0.5 * motivation
        + 0.3 * prior_gpa
    )
    prep_prob = 1 / (1 + np.exp(-prep_logit))
    prep_course = rng.binomial(1, prep_prob)

    # Mediator: hours studied (only affected by prep course and motivation)
    hours_studied = (
        10
        + 11 * prep_course
        + 3 * motivation
        + rng.normal(0, 3, n)
    ).clip(0, 50)

    # Outcome: SAT score (400-1600 scale)
    # School Quality, Motivation, GPA -> SAT Score directly
    # Prep Course -> Hours Studied -> SAT Score (causal pathway)
    sat_score = (
        1000
        + 50 * school_quality
        + 75 * motivation
        + 60 * prior_gpa
        + 5 * hours_studied   # hours -> score (the causal pathway)
        + rng.normal(0, 60, n)
    ).clip(400, 1600)

    return {
        "parents_ed": parents_ed,
        "family_income": family_income,
        "school_quality": school_quality,
        "motivation": motivation,
        "prior_gpa": prior_gpa,
        "prep_course": prep_course,
        "hours_studied": hours_studied,
        "sat_score": sat_score,
        "prep_prob": prep_prob,
        "n": n,
    }


if __name__ == "__main__":
    data = simulate_sat()
    treated = data["prep_course"] == 1
    print(f"N = {data['n']}")
    print(f"Prep rate: {treated.mean():.1%}")
    print(f"Naive diff: "
          f"{data['sat_score'][treated].mean() - data['sat_score'][~treated].mean():.1f} pts")
    print(f"Mean SAT (prep):    {data['sat_score'][treated].mean():.0f}")
    print(f"Mean SAT (no prep): {data['sat_score'][~treated].mean():.0f}")
