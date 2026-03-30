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

When frontdoor=False (default), Motivation also directly affects Hours Studied.
When frontdoor=True, that path is removed so the front-door criterion holds:
  the only path from Prep to SAT goes through Hours Studied, and Motivation
  does not affect Hours except through Prep.

True causal effect of Prep Course on SAT Score (via Hours Studied): ~55 pts.
"""

import numpy as np

SEED = 42
FRONTDOOR_SEED = 271


def simulate_sat(n=10_487, seed=SEED, frontdoor=False):
    """Return a dict of arrays with the simulated SAT dataset.

    Parameters
    ----------
    frontdoor : bool
        If True, remove the Motivation -> Hours Studied path so the
        front-door criterion holds for Prep -> Hours -> SAT.
    """

    rng = np.random.default_rng(seed)

    # Demographics (not part of the causal DAG, just for realism)
    female = rng.binomial(1, 0.52, n)  # slightly more female

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

    # School Quality + Motivation -> GPA (z-score used internally)
    gpa_z = (
        0.3 * school_quality
        + 0.35 * motivation
        + rng.normal(0, 0.5, n)
    )
    # Rescale to realistic college-applicant GPA (2.5 – 4.5)
    prior_gpa = (3.5 + 0.4 * gpa_z).clip(2.5, 4.5)

    # Treatment assignment (self-selection)
    # Family Income, Motivation, GPA -> Prep Course
    # Use gpa_z so coefficients stay on the same scale
    prep_logit = (
        -0.8
        + 0.4 * inc_z
        + 0.5 * motivation
        + 0.3 * gpa_z
        + 0.1 * female
    )
    prep_prob = 1 / (1 + np.exp(-prep_logit))
    prep_course = rng.binomial(1, prep_prob)

    # Mediator: hours studied
    # When frontdoor=True, motivation does NOT directly affect hours,
    # so the front-door criterion holds for Prep -> Hours -> SAT.
    motivation_on_hours = 0 if frontdoor else 3
    hours_studied = (
        10
        + 11 * prep_course
        + motivation_on_hours * motivation
        + rng.normal(0, 3, n)
    ).clip(0, 50)

    # Outcome: SAT score (400-1600 scale)
    # School Quality, Motivation, GPA -> SAT Score directly
    # Prep Course -> Hours Studied -> SAT Score (causal pathway)
    sat_score = (
        1000
        + 50 * school_quality
        + 75 * motivation
        + 60 * gpa_z
        + 5 * hours_studied   # hours -> score (the causal pathway)
        + rng.normal(0, 60, n)
    ).clip(400, 1600)

    return {
        "female": female,
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
