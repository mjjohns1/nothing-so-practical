---
title:       "Dread Risk and Driving"
subtitle:    "Twenty-five years of trying to answer a deceptively hard question"
description: "Did fear of flying after September 11 kill more Americans on the road than died on the planes? Twenty-five years on, the evidence points in one direction. The precise number is another matter."
date:        2026-03-07
author:      "MJ"
image:       ""
tags:        ["causal inference", "behavioral science"]
categories:  []
draft:       false
---

The September 11 attacks killed nearly 3,000 people. In the months that followed, as the country processed what had happened, a secondary question emerged among researchers studying risk and behavior: could the fear response itself be deadly?

Americans avoided flying after the attack. Revenue passenger miles fell 20% in October 2001, 17% in November, and 12% in December compared with the year before. Some of that was practical. Airline schedules were disrupted, airspace was closed and security lines emerged where there had been none. But fear was certainly a factor — and fear has a well-documented tendency to mismatch the actual distribution of risk.

Psychologists have a name for the particular dread that plane crashes and terrorist attacks trigger. Public judgments about hazards don't track statistical probability. Instead, people assess risk along two dimensions: how mysterious a hazard feels, and how much dread it generates. Dread hazards feel uncontrollable, catastrophic in scale, capable of killing large numbers of people at once. Plane crashes and terrorist attacks score near the top of that scale. Car accidents score near the bottom, even though they kill roughly 40,000 Americans a year.

If enough people responded to September 11 by driving instead of flying, they traded a vanishingly small risk for a much larger one. In 2004, Gigerenzer estimated that there were roughly 350 excess traffic deaths in the three months following the attacks, possibly more than the number who died on the four hijacked planes.

That number still appears in discussions of dread risk and behavioral responses to disaster. But it rests on a simple before-and-after comparison applied to three months of data. A contemporaneous reanalysis challenged the finding, arguing the effect was smaller and less robust once other factors were considered. The question was never fully resolved.

Twenty-five years later, with better data and better methods, here's where things stand. The direction of the effect is probably right. The precision of the original estimate never was.

## Estimating Excess Fatalities

The original approach was straightforward. Compare monthly fatal traffic crash counts for October through December 2001 to the average of those same months in the preceding five years. If 2001 runs above the historical range, the excess is attributed to the shock.

We can replicate this using FARS microdata directly.

{{< figure src="/img/dread-risk/fig1_replication.png" caption="Monthly fatal traffic crashes in 2001 (black squares) versus the 1996-2000 mean (gray line) and range (vertical bars). The dashed red line marks September 11." class="img-center" width="90%" >}}

January through September, 2001 sits within the historical range. October through December, all three months land at or above the top of it. November shows the largest jump, with 193 more fatal crashes than the baseline average. Our FARS data produces slightly different totals than the original paper (37,862 fatal crashes in 2001 versus 37,795), reflecting minor data revisions over two decades.

This is functionally an interrupted time series design — the simplest version of one. The original analysis doesn't model trend or seasonality explicitly; it just compares 2001 to a five-year mean. The method assumes the pre-intervention trend would have continued unchanged without the event, and that the event came as a surprise with no anticipatory behavioral changes beforehand. Its validity rests on whether anything else changed at the same time that could explain the spike.

Quite a lot changed. September 11 disrupted transportation networks, deepened an existing recession, and produced widespread psychological distress, including increases in alcohol consumption. Any of these could affect fatality rates independently of mode substitution.

But there's a more basic question: Is the Q4 2001 spike actually unusual?

### A Bayesian Interrupted Time Series

To put the original analysis on firmer ground, we fit a Bayesian interrupted time series (ITS) model. It includes a linear trend and monthly seasonal indicators, trained on the pre-intervention period (January 1996 through September 2001), and generates counterfactual predictions for October through December 2001 with full posterior uncertainty. September 2001 is included in the pre-period, consistent with the original paper's framing. Changing it doesn't materially affect results.

{{< figure src="/img/dread-risk/its_causalpy.png" caption="Bayesian interrupted time series analysis. Top: observed vs. counterfactual with 95% credible interval. Middle: monthly causal impact. Bottom: cumulative excess fatal crashes." class="img-center" width="90%" >}}

The model estimates 400 cumulative excess fatal crashes in October through December 2001. This is excess fatal *crashes*, not fatalities. The original paper converted to fatalities by multiplying by the crashes-to-fatalities ratio of roughly 1.11.

### Placebo Tests

A placebo test applies the same model to a year when nothing happened. If the model is well-calibrated, fake interventions should produce effects near zero. We ran the identical specification with fake intervention dates in October of 1998, 1999, and 2000.

{{< figure src="/img/dread-risk/placebo_tests.png" caption="Placebo tests. The same ITS model run with fake intervention dates in 1998-2000 (blue) versus the actual 2001 date (red). All intervals are two-sided 95% HDIs." class="img-center" width="90%" >}}

The 2000 placebo is a problem. The model confidently estimates -152 crashes per month (95% HDI [-222, -78]), a large spurious negative effect in a year when nothing happened. The 1998 and 1999 placebos are smaller and include zero in their intervals. None of these are real effects. They're year-to-year variation the model is misreading as an intervention signal.

The 2001 estimate is the largest positive outlier, which is reassuring. But the placebos show that a 3-month window is too short for this model to reliably separate a real behavioral shift from ordinary quarterly noise. The tight credible intervals overstate our confidence. The model also assumes conditionally independent errors after accounting for trend and seasonality. If monthly crash counts are autocorrelated (plausible, given weather, economic conditions, and other persistent factors), the true uncertainty is wider still. The original paper's chi-squared test, applied to three data points against a five-year average, has the same problem.

## What Happens When We Look Further

The 3-month analysis is fragile. The stronger test is the longer window. A temporary behavioral response (people avoiding flying out of fear) should produce elevated crash counts that fade as air travel normalized. Airlines reported steady recovery through 2002 and into 2003. If the effect were real and specifically driven by dread risk, it should accumulate and then decay.

### The Extended Timeline

We fit the same ITS model with the post-intervention window extended through December 2004.

{{< figure src="/img/dread-risk/its_extended.png" caption="Extended ITS analysis through 2004. The cumulative impact panel shows excess fatal crashes accumulating through the post-period." class="img-center" width="90%" >}}

| Quarter | Avg Monthly Excess |
|:--------|------------------:|
| 2001 Q4 | +136 |
| 2002 Q1 | +211 |
| 2002 Q2 | +104 |
| 2002 Q3 | +95 |
| 2002 Q4 | -30 |
| 2003 Q1 | +18 |
| 2003 Q2 | +106 |
| 2003 Q3 | +120 |
| 2003 Q4 | +127 |
| 2004 Q1 | +118 |
| 2004 Q2 | +158 |
| 2004 Q3 | +59 |
| 2004 Q4 | +23 |

These are observed values minus the posterior mean counterfactual. They're point differences, not full posterior distributions. The effect peaked in early 2002, dipped briefly in Q4 2002, then remained persistently positive through 2004. That's not the clean accumulate-and-decay pattern a dread risk story predicts. Air travel recovered. The excess didn't disappear.

One interpretation: the standard ITS assumes the pre-period trend continues unchanged into the counterfactual. If the model is projecting a trajectory that wouldn't have held anyway, the excess gets inflated by model error rather than intervention effect.

### A Piecewise Model

A piecewise ITS addresses this directly. Rather than projecting the pre-period trend forward, it fits one model to the full time series and explicitly estimates whether the slope changed at the intervention date alongside any level change. Both the immediate jump and the change in trajectory are estimated at once.

{{< figure src="/img/dread-risk/its_piecewise.png" caption="Piecewise interrupted time series. The model estimates a level change and slope change at October 2001, fit on the full 1996-2004 series." class="img-center" width="90%" >}}

Across the 39-month post-intervention window, the piecewise model estimates an average effect of +96 excess crashes per month (95% HDI: +26 to +164), with a posterior probability of a positive effect of 0.996. The cumulative estimate is roughly 3,700 excess crashes over the period.

This formulation is more conservative than straight extrapolation. It can absorb some of the persistent excess into a slope change rather than treating it all as an intervention effect. That it still finds a clear positive effect across nearly three years is the strongest temporal evidence in the analysis.

## Geographic Heterogeneity

If the mechanism is mode substitution, the effect should be stronger in states where more people fly. We split states into two groups using 2001 FAA enplanement data and compared October through December 2001 fatal crashes against the 1996-2000 baseline.

Raw percentages are misleading here. Colorado shows a 40% increase. That's 18 crashes against a monthly baseline of 46. Hawaii shows 45%. These numbers can't sit alongside California or Texas without adjustment. To handle this, we fit a Bayesian weighted model on state-level change scores, using the standard error of the change score as the likelihood variance. States with stable, high-volume baselines drive the estimates. Small noisy states contribute little.

{{< figure src="/img/dread-risk/state_hierarchical.png" caption="Left: state-level change scores (dot size proportional to baseline crash volume). Right: posterior distribution of the weighted group contrast." class="img-center" width="90%" >}}

The weighted group difference is +4.3 crashes per month (95% credible interval: +1.3 to +7.2). High air travel states added roughly 5 more crashes per month against their pre-period baseline; other states added less than 1. The posterior probability that the group difference is positive is 0.998.

The grouping is binary and somewhat arbitrary. The 15th and 16th states by enplanement volume aren't meaningfully different from each other. And the same 3-month window problem applies here too. Still, this is the clearest piece of evidence in the analysis. It's the geographic pattern mode substitution predicts, and it holds up after correcting for small-state noise.

### Road Type

The original paper noted that rural interstate VMT spiked 5.3% after September 11, consistent with long-distance driving substituting for flights. If that's the mechanism, the excess should show up on interstates.

FARS classifies crashes by road functional class. We grouped rural and urban interstates together and compared against non-interstate roads.

{{< figure src="/img/dread-risk/road_type.png" caption="Fatal crashes by road type in 2001 vs. 1996-2000 baseline. Left: all interstates. Right: non-interstate roads." class="img-center" width="90%" >}}

Interstates saw a 2.7% increase (+31 crashes), while non-interstate roads saw 4.3% (+371 crashes). Over 90% of the excess accumulated off the interstate system. Interstates are the safest roads per mile, so extra highway miles produce fewer additional fatalities than the same miles on arterials and local roads. The comparison is also imprecise, since the 5.3% VMT figure covers rural interstates only while the crash figure combines rural and urban. The finding is ambiguous rather than contradictory, consistent with mode substitution but not uniquely explained by it.

## What This Tells Us

The original paper appeared three years after the attacks, asked the right question, and got the direction roughly right. It also produced a specific number that the data can't support at that precision. The same methodology applied to control years fires false alarms. The contemporaneous reanalysis found the effect smaller and less robust. The literature that followed reached broadly consistent but varying conclusions across different methods and time windows.

Twenty-five years on, the most defensible summary is that there probably was a real increase in traffic fatalities following September 11, concentrated in states with the most air travel, persisting for at least several months and possibly longer. The piecewise model, which allows the trajectory to change rather than just the level, finds a positive effect across 39 months with high posterior confidence. The geographic evidence holds up after correcting for noise in small-state estimates.

What we can't say with confidence is how large the effect was, how long it lasted, or how much of it was specifically driven by mode substitution versus other disruptions the attacks set in motion. The methods agree on direction. They diverge on magnitude. Some evidence fits the story neatly; some doesn't. That's what causal inference looks like on a question where you can't run an experiment, where the intervention changed everything at once, and where the data is a monthly national aggregate.

The 350-deaths figure is memorable. "A real effect, concentrated in the right places, magnitude uncertain" is harder to quote. It's closer to what the evidence shows.

----
##### References

Gigerenzer, G. (2004). Dread Risk, September 11, and Fatal Traffic Accidents. **Psychological Science**, 15(4), 286-287.

Sivak, M., & Flannagan, M. J. (2004). Consequences for road traffic fatalities of the reduction in flying following September 11, 2001. **Transportation Research Part F**, 7(4–5), 301–305.

Slovic, P. (1987). Perception of Risk. **Science**, 236(4799), 280-285.
