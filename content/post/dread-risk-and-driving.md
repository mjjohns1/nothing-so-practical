---
title:       "Dread Risk and Driving"
subtitle:    "Replicating and extending a classic study on dread risk after 9/11"
description: "Did fear of flying after September 11 kill more Americans on the road than died on the planes? An updated analysis using modern causal inference methods."
date:        2026-04-03
author:      "MJ"
image:       ""
tags:        ["causal inference", "behavioral science"]
categories:  []
draft:       false
---

Most people know, in the abstract, that flying is safer than driving. Per mile traveled, the fatality rate for commercial aviation is at least an order of magnitude lower than for car travel. The actual risk of dying on any given flight is vanishingly small. And yet plenty of people are nervous flyers who'd rather spend twelve hours on the road than three hours in the air. Rational risk assessment and emotional risk perception are different things.

This gap has a name in the risk perception literature: dread risk. Paul Slovic and colleagues showed in the 1980s that public judgments about hazards don't track statistical probability. Instead, people assess risk along two dimensions: how unknown or mysterious a hazard feels, and how much dread it generates. Dread hazards feel uncontrollable, catastrophic in scale, and capable of wiping out large numbers of people at once. Plane crashes, nuclear accidents, and terrorist attacks all score high on dread. Car accidents score low, even though they kill far more people. The result is a systematic mismatch between perceived and actual risk.

September 11, 2001 was a dread risk event at an extreme scale. After the attacks, Americans avoided flying and drove instead. Revenue passenger miles dropped 20% in October 2001, 17% in November, and 12% in December compared with the same months in 2000. Part of this was rational: reduced flight offerings, longer security lines, disrupted schedules. But fear was also a factor, a reasonable response to an unprecedented attack that made sense emotionally even when the numbers said otherwise.

More people on the road means more accidents and more fatalities. Avoiding air travel by driving instead trades a very low risk for a much higher one. If enough people made that switch, the death toll on American highways could have exceeded the number who died on the four hijacked planes. That's the hypothesis Gigerenzer set out to test.

## Estimating Excess Fatalities

Gigerenzer set out to examine this possibility by comparing traffic fatality rates between October and December of 2001 to those same months in the preceding 5 years. In addition to the reduction in miles flown, Vehicle miles traveled (VMT) in October through December 2001 were 2.9% higher than the same months in 2000, compared with a 0.9% average increase in the months before September. The remaining question is the central hypothesis of his study: did the extra driving cause extra deaths?

To test this hypothesis, he analyzed monthly fatal traffic crash counts from NHTSA's Traffic Safety Facts reports for 1996 through 2001. The approach was simple. Compute the monthly average for 1996-2000 as a baseline, then compare 2001 against it. Before September, 2001 tracks the baseline closely, with an average deviation of just 9 fatal crashes per month (0.3% of the monthly total). After September, the October through December counts jump above the baseline.

Assuming the last three months of 2001 would have continued the same small average increase of 9 crashes per month seen in January through August, the difference between this expected value and the observed value is the estimated excess: 67 + 163 + 87 = 317 excess fatal crashes across October, November, and December. Multiplying by the ratio of fatalities to crashes (42,116 / 37,795) gives roughly 353 excess deaths.

We can replicate this analysis using FARS microdata.

{{< figure src="/img/dread-risk/fig1_replication.png" caption="Monthly fatal traffic crashes in 2001 (black squares) versus the 1996-2000 mean (gray line) and range (vertical bars). The dashed red line marks September 11." class="img-center" width="90%" >}}

The pattern matches. January through September, 2001 sits within the historical range. October through December, all three months are at or above the top of the range. November shows the largest jump, with 193 more fatal crashes than the baseline average. Our FARS data produces slightly different totals than the original paper (37,862 fatal crashes in 2001 versus the paper's 37,795), reflecting minor data revisions over the past two decades.

The paper is asking a causal question: did fear of flying cause excess traffic deaths? The analysis is essentially a before-and-after comparison with no control group, applied to aggregate monthly counts. This is an interrupted time series design. The method itself is well-established. It assumes the pre-intervention trend would have continued unchanged in the absence of the event, and that the event came as a surprise with no anticipatory behavioral changes beforehand. Its validity depends primarily on the assumption that nothing else changed at the same time that could explain the spike. Is that a valid assumption?

September 11 didn't just change flying behavior. It disrupted transportation networks, altered commuting patterns in the Northeast, triggered a recession, and produced widespread psychological distress. Alcohol consumption patterns shifted too, with some evidence of increased drinking in the months following the attacks. Any of these could affect traffic fatality rates independently of mode substitution.

But even setting aside confounders, there's a more basic question: is the observed Q4 2001 spike actually unusual, or does year-to-year variation in quarterly crash counts routinely produce deviations of this size?

### A Bayesian Interrupted Time Series

To put the original analysis on firmer ground, we fit a Bayesian interrupted time series (ITS) model. The model includes a linear trend and monthly seasonal indicators, fit on the pre-intervention period (January 1996 through September 2001). It generates counterfactual predictions for October through December 2001 with full posterior uncertainty. September 2001 is included in the pre-intervention period, but 20 of its 30 days fell after the attacks. This is consistent with the original paper's framing, and changing it doesn't materially affect the results. If post-attack driving increased crash risk in September, including it in the pre-period biases the counterfactual upward and understates the October–December effect; if people stayed home immediately after the attacks, the bias runs in the other direction.

{{< figure src="/img/dread-risk/its_causalpy.png" caption="Bayesian interrupted time series analysis. Top: observed vs. counterfactual with 95% credible interval. Middle: monthly causal impact. Bottom: cumulative excess fatal crashes." class="img-center" width="90%" >}}

The model estimates 400 cumulative excess fatal crashes in October through December 2001, with a 95% highest density interval of roughly 200 to 580. Our estimate of 400 excess fatal *crashes* is distinct from the original paper's 353 excess *fatalities*. The paper arrives at its fatality count by multiplying 317 excess crashes by the ratio of fatalities to fatal crashes (roughly 1.11).

### Placebo Tests

A placebo test runs the same model but places a fake intervention at a time when no effect should exist. If the model is well-calibrated, placebo years should produce effects equivalent to zero. We ran the identical ITS specification pretending September 11 happened in October of 1998, 1999, and 2000. (The 1997 placebo was attempted but produced 507 sampler divergences with only 21 months of pre-period data — not enough for the model to learn seasonal patterns reliably — so it's excluded from the comparison.)

{{< figure src="/img/dread-risk/placebo_tests.png" caption="Placebo tests. The same ITS model is run with fake intervention dates in 1998-2000 (blue) versus the actual 2001 date (red). All intervals are two-sided 95% HDIs." class="img-center" width="90%" >}}

The 2000 placebo stands out: the model confidently estimates -152 crashes per month (95% HDI [-222, -78]), a large spurious negative effect. The 1998 and 1999 placebos include zero in their HDIs and produce smaller point estimates. These aren't real effects. They're year-to-year variation the model mistakes for an intervention.

One caveat: the placebo pre-periods aren't all the same length. The 1998 placebo trains on just 33 months, while 2001 uses 69. Shorter pre-periods give the model less data to learn seasonal patterns, which may inflate false positive rates for the earlier placebos. Still, even the 2000 placebo, with 57 months of training data, produces a large spurious effect.

The 2001 effect is the largest positive outlier, and it's the only year with a large positive effect. That's worth noting. But the placebos demonstrate that a 3-month window is too short for this model to reliably distinguish a real behavioral shift from ordinary quarterly noise. The tight credible intervals overstate our confidence — and the model assumes conditionally independent errors after accounting for trend and seasonality. If monthly crash counts are positively autocorrelated (a reasonable expectation given weather, economic conditions, and other persistent drivers), the true uncertainty is wider still. The original paper's chi-squared test, applied to three data points against a five-year average, suffers from the same problem.

## Evidence That Survives Scrutiny

The 3-month analysis is fragile. But we have data through 2004, which allows a stronger test. If the 2001 spike were just noise, it wouldn't persist into 2002. A real behavioral shift should show up as sustained excess that eventually fades as people resumed flying. What we actually find is more complicated.

### The Extended Timeline

We fit the same ITS model but include all data through December 2004 in the post-intervention window.

{{< figure src="/img/dread-risk/its_extended.png" caption="Extended ITS analysis through 2004. The cumulative impact panel shows excess fatal crashes accumulating through the post-period." class="img-center" width="90%" >}}

| Quarter | Avg Monthly Excess (posterior mean) |
|:--------|-----------------------------------:|
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

These are observed values minus the posterior mean counterfactual — point differences, not full posterior effect distributions. The credible intervals visible in the figure above show the uncertainty around the counterfactual prediction and widen as the projection extends further from the pre-period.

The effect peaked in early 2002, dipped briefly in Q4 2002, then rebounded through 2003 and remained positive into 2004. This is not the clean accumulate-and-decay pattern a dread risk story would predict. A behavioral response tied to fear of flying should fade as air travel normalized, and airlines did report steady recovery through 2002 and 2003. The persistent positive values through 2004 suggest the linear trend model may not fully capture the pre-period trajectory, or that other post-9/11 factors affected traffic fatality rates over a longer horizon than mode substitution alone can explain.

The extended analysis goes further than the original paper could, and it provides additional evidence that the Q4 2001 spike reflected a real shift. But the longer window also raises questions the original paper didn't have to answer.

### Geographic Heterogeneity

If the mechanism is people driving instead of flying, the effect should be stronger in states where more people fly. We split states into two groups based on 2001 passenger enplanement volume (FAA data) and compared October through December 2001 fatal crashes against the 1996-2000 baseline.

The raw percentages are noisy: small states swing wildly on a handful of crashes. Colorado shows a 40% increase, but its monthly baseline is 46 crashes — a difference of 18 crashes. Hawaii shows 45%. These numbers don't belong in the same comparison as California or Texas without adjustment. To handle this, we fit a simple Bayesian weighted model on state-level change scores, using each state's pre-period standard error as the likelihood variance. States with stable, high-volume baselines pull the estimates; small noisy states contribute little.

{{< figure src="/img/dread-risk/state_hierarchical.png" caption="Left: state-level change scores (dot size proportional to baseline crash volume). Right: posterior distribution of the weighted DiD estimate." class="img-center" width="90%" >}}

The weighted difference-in-differences estimate is +4.3 crashes per month (95% HDI: +3.1 to +5.5), with P(DiD > 0) = 1.00. High air travel states added roughly 5 more crashes per month in Oct-Dec 2001 than their pre-period baseline; other states added less than 1. The group separation holds up after weighting out the noise from small states.

The usual caveats apply. The grouping is binary and somewhat arbitrary — the 15th and 16th states by enplanement volume are not meaningfully different. This is descriptive, not causal. And the same 3-month window that the placebo tests flagged as unreliable is at work here too. Still, the concentration in high-air-travel states is the clearest supporting evidence in the analysis.

### Road Type

The original paper notes that rural interstate VMT spiked 5.3% after September 11, consistent with more long-distance driving. If the fatality increase came from mode substitution, it should show up on interstates.

FARS classifies crashes by road functional class. We grouped rural interstates (code 1) and urban interstates (code 11) together and compared against non-interstate roads.

{{< figure src="/img/dread-risk/road_type.png" caption="Fatal crashes by road type in 2001 vs. 1996-2000 baseline. Left: all interstates. Right: non-interstate roads." class="img-center" width="90%" >}}

Interstates saw a modest 2.7% increase (+31 crashes), while non-interstate roads saw 4.3% (+371 crashes). Over 90% of the excess occurred off the interstate system. Interstates are the safest roads per mile, so extra interstate miles produce fewer additional fatalities than the same miles on arterials and local roads. The 2.7% crash increase against a 5.3% VMT spike implies a sub-unit elasticity of fatal crashes to miles driven — though this comparison is imprecise, since the 5.3% VMT figure covers rural interstates only while the 2.7% crash figure combines rural and urban interstates. This is common in traffic safety research (doubling VMT does not double fatalities), so the finding is ambiguous rather than contradictory. It's consistent with mode substitution, but also consistent with more benign explanations like increased travel on already-busy routes where marginal risk per mile is lower.

## What This Tells Us

The original paper asked the right question and got the direction of the answer roughly right. Traffic fatalities did increase after September 11, and the increase concentrated in high air travel states.

But the original analysis is too thin to support the precision of its headline claim. The chi-squared test on three data points against a five-year average isn't strong evidence. Our placebo tests show that the same methodology flags large "effects" in years when nothing happened. The 350-deaths number implies a certainty that the data can't support. Sivak and Flannagan raised similar objections in a direct reanalysis published the same year, arguing the effect was smaller and less robust when other factors were considered.

The extended analysis adds evidence that the Q4 2001 spike was real, but complicates the story. The effect doesn't decay cleanly as a behavioral dread-risk response should. Persistent positive values through 2003 and 2004 suggest something else is going on alongside mode substitution — whether model misspecification, longer-lasting economic disruption, or other post-9/11 factors. The geographic evidence is the strongest piece. A Bayesian weighted DiD — accounting for the noise in small-state estimates — finds that high air travel states added roughly 5 more fatal crashes per month than their pre-period baseline, compared to less than 1 for other states. The posterior probability that the group difference is positive is effectively 1.

"A real increase in traffic fatalities, concentrated in high-air-travel states, following September 11" is a more defensible summary than "exactly 350 excess deaths in three months." It's less quotable. It's closer to what the evidence shows.

----
##### References

Gigerenzer, G. (2004). Dread Risk, September 11, and Fatal Traffic Accidents. **Psychological Science**, 15(4), 286-287.

Sivak, M., & Flannagan, M. J. (2004). Consequences for road traffic fatalities of the reduction in flying following September 11, 2001. **Transportation Research Part F**, 7(4–5), 301–305.

Slovic, P. (1987). Perception of Risk. **Science**, 236(4799), 280-285.