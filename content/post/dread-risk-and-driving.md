---
title:       "Dread Risk and Driving"
subtitle:    "Replicating and extending a classic study on dread risk after 9/11"
description: "Did fear of flying after September 11 kill more Americans on the road than died on the planes? An updated analysis with modern using causal inference methods."
date:        2026-04-03
author:      "MJ"
image:       ""
tags:        ["causal inference", "behavioral science"]
categories:  []
draft:       true
---

## Dread Risk and Driving

Dread risk is defined as the fear of catastrophic but rare events (ref). [summarize research on dread risk?]

The terrorist attack on September 11, 2001 represent just such an event. After the attack, Americans avoided flying and drove instead. Revenue passenger miles dropped 20% in October 2001, 17% in November, and 12% in December compared with the same months in 2000. This shouldn't be surprising. Reductions in in flight offerings and increased security measures made flying less convenient in the months afterward. Without a doubt, lingering fear and anxiety about follow-up attacks also contributed to the decision to drive instead of fly.

We've all heard that flying is safer than driving, at least statistically. [some stats about per capita mortality rate]. More people on the road means more accidents and more fatalities. Shifting from flying to driving increases the relative risk of injury and death. Ironically, avoiding air travel after 911 and driving instead could have been a fatal mistake.

## Estimating Excess Fatalities

Gigerenzer set out to examine this possibility by comparing traffic fatality rates between October and December of 2001 to those sames months in the preceeding 5 years. In addition to the reduction in miles flown, Vehicle miles traveled (VMT) in October through December 2001 were 2.9% higher than the same months in 2000, compared with a 0.9% average increase in the months before September. The remaining question is central hypothesis of his study: did the extra driving cause extra deaths?

To test this hypothesis, he analyzed monthly fatal traffic crash counts from NHTSA's Traffic Safety Facts reports for 1996 through 2001. The approach was simple. Compute the monthly average for 1996-2000 as a baseline, then compare 2001 against it. Before September, 2001 tracks the baseline closely, with an average deviation of just 9 fatal crashes per month (0.3% of the monthly total). After September, the October through December counts jump above the baseline.

Assuming the last three months of 2001 would have continued the same small average increase of 9 crashes per month seen in January through August, the difference between this expected value and the observed value is the estimated excess: 67 + 163 + 87 = 317 excess fatal crashes across October, November, and December. Multiplying by the ratio of fatalities to crashes (42,116 / 37,795) gives roughly 353 excess deaths.

We can replicate this analysis using FARS microdata.

{{< figure src="/img/dread-risk/fig1_replication.png" caption="Monthly fatal traffic crashes in 2001 (black squares) versus the 1996-2000 mean (gray line) and range (vertical bars). The dashed red line marks September 11." class="img-center" width="90%" >}}

The pattern matches. January through September, 2001 sits within the historical range. October through December, all three months are at or above the top of the range. November shows the largest jump, with 193 more fatal crashes than the baseline average. Our FARS data produces slightly different totals than the original paper (37,862 fatal crashes in 2001 versus the paper's 37,795), reflecting minor data revisions over the past two decades.

The paper is asking a causal question: did fear of flying cause excess traffic deaths? The analysis is essentially a before-and-after comparison with no control group, applied to aggregate monthly counts. This is an interrupted time series design. The method itself is well-established. [describe assumptions]. Its validity depends primarily on the assumption that nothing else changed at the same time that could explain the spike. Is that a valid assumption?

September 11 didn't just change flying behavior. It disrupted transportation networks, altered commuting patterns in the Northeast, triggered a recession, and produced widespread psychological distress. Alcohol consumption patterns shifted too, with some evidence of increased drinking in the months following the attacks. Any of these could affect traffic fatality rates independently of mode substitution.

But even setting aside confounders, there's a more basic question: is the observed Q4 2001 spike actually unusual, or does year-to-year variation in quarterly crash counts routinely produce deviations of this size?

### A Bayesian Interrupted Time Series

To put the original analysis on firmer ground, we fit a Bayesian interrupted time series (ITS) model. The model includes a linear trend and monthly seasonal indicators, fit on the pre-intervention period (January 1996 through September 2001). It generates counterfactual predictions for October through December 2001 with full posterior uncertainty. September 2001 is included in the pre-intervention period, but 20 of its 30 days fell after the attacks. This is consistent with the original paper's framing, and changing it doesn't materially affect the results, but it means the pre-period is slightly contaminated by any post-attack behavioral shift.

{{< figure src="/img/dread-risk/its_causalpy.png" caption="Bayesian interrupted time series analysis. Top: observed vs. counterfactual with 95% credible interval. Middle: monthly causal impact. Bottom: cumulative excess fatal crashes." class="img-center" width="90%" >}}

The model estimates 353 cumulative excess fatal crashes in October through December 2001, with a 95% highest density interval of roughly 300 to 406. Our estimate of 353 excess fatal *crashes* is distinct from the original paper's 353 excess *fatalities*. The paper arrives at its fatality count by multiplying 317 excess crashes by the ratio of fatalities to fatal crashes (roughly 1.11). The near-identical headline numbers are a coincidence.

### Placebo Tests

A placebo test runs the same model but places a fake intervention at a time when no effect should exist. If the model is well-calibrated, placebo years should produce effects equivalent to zero. We ran the identical ITS specification pretending September 11 happened in October of 1997, 1998, 1999, and 2000.

{{< figure src="/img/dread-risk/placebo_tests.png" caption="Placebo tests. The same ITS model is run with fake intervention dates in 1997-2000 (blue) versus the actual 2001 date (red). Error bars show 95% HDI." class="img-center" width="90%" >}}

The estimate for 2000 produces a large effect. The model confidently estimates that Q4 1997 had 146 fewer fatal crashes per month than expected, and Q4 2000 had 175 fewer. These aren't real effects. They're just year-to-year variation that the model mistakes for an intervention.

One caveat: the placebo pre-periods aren't all the same length. The 1997 placebo trains on just 21 months, while 2001 uses 69. Shorter pre-periods give the model less data to learn seasonal patterns, which may inflate false positive rates for the earlier placebos. Still, even the 2000 placebo, with 57 months of training data, produces a large spurious effect.

The 2001 effect is the largest positive outlier, and it's the only year with a large positive effect. That's worth noting. But the placebos demonstrate that a 3-month window is too short for this model to reliably distinguish a real behavioral shift from ordinary quarterly noise. The tight credible intervals overstate our confidence. The original paper's chi-squared test, applied to three data points against a five-year average, suffers from the same problem.

## Evidence That Survives Scrutiny

The 3-month analysis is fragile. But we have data through 2004, which allows a stronger test. If the 2001 spike were just noise, it wouldn't persist into 2002. If it reflects a real behavioral shift, the excess should accumulate over time before fading as people resumed flying.

### The Extended Timeline

We fit the same ITS model but include all data through December 2004 in the post-intervention window.

{{< figure src="/img/dread-risk/its_extended.png" caption="Extended ITS analysis through 2004. The cumulative impact panel shows excess fatal crashes continuing to accumulate through mid-2002 before leveling off." class="img-center" width="90%" >}}

| Quarter | Avg Monthly Excess (posterior mean) |
|:--------|-----------------------------------:|
| 2001 Q4 | +118 |
| 2002 Q1 | +148 |
| 2002 Q2 | +69 |
| 2002 Q3 | +70 |
| 2002 Q4 | -63 |
| 2003+ | Mixed around zero |

These are posterior mean point estimates. The full posterior distributions are visible in the figure above, where the credible intervals widen as the projection extends further from the pre-period.

The effect peaked in early 2002 and faded by the second half of that year, roughly 9 to 12 months after the attacks. By 2003, the monthly excess bounces around zero. This pattern is harder to dismiss as noise. Quarterly variation could explain a single 3-month spike, but it can't easily explain a sustained elevation that gradually decays over the same period that airlines reported depressed passenger traffic.

The extended analysis is the most convincing evidence in favor of the dread-risk hypothesis, and it's one the original paper couldn't run.

### Geographic Heterogeneity

If the mechanism is people driving instead of flying, the effect should be stronger in states where more people fly. We split states into two groups based on passenger enplanement volume and compared October through December 2001 fatal crashes against the 1996-2000 baseline.

{{< figure src="/img/dread-risk/state_excess.png" caption="Percentage change in fatal crashes (Oct-Dec 2001 vs. baseline) by state. Red bars are high air travel states." class="img-center" width="90%" >}}

High air travel states saw a 6.7% increase in fatal crashes. All other states saw 0.9%. Among the larger states: New York (+17%), Georgia (+17%), Pennsylvania (+13%), and Colorado (+40%, though with a smaller baseline). This is the pattern you'd predict from mode substitution, and it's a pattern the original paper never tested. But these are raw group averages without formal uncertainty quantification on the difference, so the gap between groups could partly reflect sampling variability.

The usual caveats apply. Small states produce noisy percentages. This is descriptive, not causal. And the same 3-month window that the placebo tests flagged as unreliable is at work here too. Still, the concentration in high-air-travel states is suggestive.

### Road Type

The original paper notes that rural interstate VMT spiked 5.3% after September 11, consistent with more long-distance driving. If the fatality increase came from mode substitution, it should show up on interstates.

FARS classifies crashes by road functional class. We grouped rural interstates (code 1) and urban interstates (code 11) together and compared against non-interstate roads.

{{< figure src="/img/dread-risk/road_type.png" caption="Fatal crashes by road type in 2001 vs. 1996-2000 baseline. Left: all interstates. Right: non-interstate roads." class="img-center" width="90%" >}}

Interstates saw a modest 2.7% increase (+31 crashes), while non-interstate roads saw 4.3% (+371 crashes). Over 90% of the excess occurred off the interstate system. Interstates are the safest roads per mile, so extra interstate miles produce fewer additional fatalities than the same miles on arterials and local roads. The 2.7% crash increase against a 5.3% VMT spike implies a sub-unit elasticity of fatal crashes to miles driven. This is common in traffic safety research (doubling VMT does not double fatalities), so the finding is ambiguous rather than contradictory. It's consistent with mode substitution, but also consistent with more benign explanations like increased travel on already-busy routes where marginal risk per mile is lower.

## What This Tells Us

The original paper asked the right question and got the direction of the answer roughly right. Traffic fatalities did increase after September 11, and the increase concentrated in high air travel states and persisted in a pattern consistent with gradually fading fear.

But the original analysis is too thin to support the precision of its headline claim. The chi-squared test on three data points against a five-year average isn't strong evidence. Our placebo tests show that the same methodology flags large "effects" in years when nothing happened. The 350-deaths number implies a certainty that the data can't support.

The stronger evidence comes from what the original paper couldn't do: extending the window through 2004 and watching the effect accumulate and decay. That sustained pattern is harder to explain away. The geographic concentration in high-air-travel states provides additional support, even if it's descriptive.

"A sustained increase in traffic fatalities, concentrated in high-air-travel states, lasting about a year after September 11" is a more defensible summary than "exactly 350 excess deaths in three months." It's less quotable. It's closer to what the evidence shows.

----
##### References

Gigerenzer, G. (2004). Dread Risk, September 11, and Fatal Traffic Accidents. **Psychological Science**, 15(4), 286-287.