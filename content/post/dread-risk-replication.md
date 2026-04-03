---
title:       "The Second Toll"
subtitle:    "Replicating and extending a classic study on dread risk after 9/11"
description: "Fear of flying after September 11 may have killed more Americans on the road than died on the planes. We update the analysis with modern causal inference methods."
date:        2026-04-03
author:      "MJ"
image:       ""
tags:        ["causal inference", "behavioral science"]
categories:  []
draft:       false
---

In 2004, a short paper in *Psychological Science* made a striking claim. After the September 11 attacks, Americans avoided flying and drove instead. The extra driving killed roughly 350 people in the three months following the attacks, more than the 266 passengers and crew who died on the four hijacked planes. Fear of a catastrophic but rare event (what psychologists call a *dread risk*) led people to substitute a more dangerous activity for a less dangerous one, and the substitution was fatal.

The paper is a two-page commentary with a single figure. It compares monthly fatal traffic crashes in 2001 against the 1996-2000 average and finds a clear spike in October, November, and December. The analysis is elegant and persuasive, but by modern standards it's also quite simple. The counterfactual is a five-year average. The uncertainty is a chi-squared test. There's no trend adjustment, no geographic breakdown, no attempt to measure how long the effect lasted.

Twenty years of better data and better tools let us do more. We replicate the original finding using crash-level microdata from NHTSA's Fatality Analysis Reporting System, then extend it with a Bayesian interrupted time series model, state-level analysis, and data through 2004.

## Replicating Figure 1

The original analysis compares the number of fatal traffic crashes per month in 2001 against the range and mean from 1996 through 2000. The logic is straightforward. If 2001 tracked the prior years before September and diverged after, the divergence is evidence of a behavioral shift.

FARS gives us individual crash records with date, location, road type, and fatality count. We aggregated these to monthly national totals for 1996-2004. Here's our replication of the original figure.

{{< figure src="/img/dread-risk/fig1_replication.png" caption="Monthly fatal traffic crashes in 2001 (black squares) versus the 1996-2000 mean (gray line) and range (vertical bars). The dashed red line marks September 11." class="img-center" width="90%" >}}

The pattern matches the original paper closely. January through September 2001, the monthly crash counts sit within or near the historical range. The average deviation from the five-year mean is small and mixed in direction. Then October, November, and December all land at or above the top of the range. November shows the largest jump, with 193 more fatal crashes than the baseline average.

Our FARS data produces slightly different totals than the original paper (37,862 fatal crashes in 2001 versus the paper's 37,795), which reflects minor data revisions over the past two decades. The story is the same.

## A Better Counterfactual

The original paper's counterfactual is the 1996-2000 monthly mean plus a small constant for the general trend. This works well enough for a two-page commentary, but it doesn't account for seasonality interactions with the trend, and it gives only a point estimate with a chi-squared test for inference.

We fit a Bayesian interrupted time series (ITS) model using CausalPy, a Python library for causal inference built on PyMC. The model includes a linear trend and monthly seasonal indicators, fit on the pre-intervention period (January 1996 through September 2001). It then generates counterfactual predictions for October through December 2001 with full posterior uncertainty.

{{< figure src="/img/dread-risk/its_causalpy.png" caption="Bayesian interrupted time series analysis. Top: observed vs. counterfactual with 95% credible interval. Middle: monthly causal impact. Bottom: cumulative excess fatal crashes." class="img-center" width="90%" >}}

The model estimates 353 cumulative excess fatal crashes in October through December 2001, with a 95% highest density interval (HDI) of roughly 300 to 406. The posterior probability of an increase is 100%. The original paper estimated 317 excess crashes. Our slightly higher estimate reflects the trend-adjusted counterfactual, which produces a tighter baseline and attributes a bit more of the deviation to the intervention rather than noise.

The bottom line is the same, but now we can say it with calibrated uncertainty. The excess is real, it's substantial, and it's not an artifact of how we constructed the baseline.

## How Long Did the Dread Last?

The original paper stops at December 2001 because that's all the data available at the time. We have data through 2004, which lets us answer a question the paper could only speculate about. How long did the excess persist?

We fit the same ITS model but include all data through December 2004 in the post-intervention window.

{{< figure src="/img/dread-risk/its_extended.png" caption="Extended ITS analysis through 2004. The cumulative impact panel shows excess fatal crashes continuing to accumulate through mid-2002 before leveling off." class="img-center" width="90%" >}}

The quarterly breakdown tells the story.

| Quarter | Avg Monthly Excess |
|:--------|-------------------:|
| 2001 Q4 | +118 |
| 2002 Q1 | +148 |
| 2002 Q2 | +69 |
| 2002 Q3 | +70 |
| 2002 Q4 | -63 |
| 2003+ | Mixed around zero |

The effect didn't end in December 2001. It actually peaked in early 2002 and didn't fade until the second half of that year, roughly 9 to 12 months after the attacks. By 2003 the monthly excess bounces around zero with no consistent direction.

This makes sense psychologically. Fear of flying didn't switch off on January 1, 2002. Airlines reported depressed passenger traffic well into 2002. The extended timeline suggests the three-month window in the original paper captured only the leading edge of a longer behavioral shift, and the total toll was considerably larger than 350.

## Where the Effect Was Strongest

If the mechanism is genuinely people driving instead of flying, the effect should be stronger in states where more people fly. We split states into two groups based on passenger enplanement volume and compared October through December 2001 fatal crashes against the 1996-2000 baseline.

{{< figure src="/img/dread-risk/state_excess.png" caption="Percentage change in fatal crashes (Oct-Dec 2001 vs. baseline) by state. Red bars are high air travel states. The excess concentrates in states where flying is common." class="img-center" width="90%" >}}

The difference is stark. High air travel states saw a 6.7% increase in fatal crashes. All other states saw just 0.9%. Among the top states: New York (+17%), Georgia (+17%), Pennsylvania (+13%), and Colorado (+40%, though with a smaller baseline). This is the pattern you'd predict if the excess fatalities came from mode substitution, and it's a pattern the original paper never tested.

Some caution is warranted with the small states. Hawaii (+45%) and DC (+29%) have low baseline crash counts, so a handful of extra crashes produces a dramatic percentage swing. The large-state results are more reliable, and they consistently support the dread-risk story.

## A Wrinkle in the Road Type Data

The original paper notes that vehicle miles traveled on rural interstates spiked 5.3% after September 11, consistent with more long-distance driving. A natural prediction follows. If the fatality increase came from people driving instead of flying, it should concentrate on interstate highways.

FARS classifies each crash by road functional class. The codes distinguish rural interstates (code 1) from urban interstates (code 11), along with arterials, collectors, and local roads in both settings. A cross-country drive uses both rural and urban interstates, so we grouped them together and compared all interstate crashes against non-interstate.

Interstates saw a modest 2.7% increase (+31 crashes), while non-interstate roads saw 4.3% (+371 crashes). Over 90% of the excess occurred off the interstate system.

{{< figure src="/img/dread-risk/road_type.png" caption="Fatal crashes by road type in 2001 vs. 1996-2000 baseline. Left: all interstates (rural + urban). Right: non-interstate roads. The post-9/11 excess concentrates on non-interstate roads." class="img-center" width="90%" >}}

This makes sense once you consider fatality rates. Interstates are the safest roads per mile driven. They carry a huge share of long-distance vehicle miles but account for only about 13% of fatal crashes nationally. A cross-country trip might be 80% interstate by distance but 80% non-interstate by fatality risk, because the dangerous parts are the arterials and local roads at each end.

The pattern is consistent with mode substitution. People drove long distances that they would otherwise have flown. The extra miles added some risk on interstates, but the deadliest portion of each trip was the non-interstate segment, and that's where the excess shows up.

## What This Tells Us

The original finding holds up. Traffic fatalities spiked after September 11, and the spike concentrated in exactly the places you'd expect if fear of flying drove people onto the roads. The Bayesian analysis puts the estimate on firmer statistical ground, with a properly constructed counterfactual and calibrated uncertainty intervals.

The extensions add nuance. The effect lasted about a year, not three months. It hit high air travel states hardest. And the road type pattern suggests the story is somewhat more complicated than pure mode substitution.

The broader lesson is the one the original paper emphasized. Dread risks distort decision-making. A catastrophic event that kills hundreds in a single moment triggers a behavioral response that a diffuse risk spread across millions of car trips does not, even when the diffuse risk is objectively larger. The September 11 attacks were a tragedy. The subsequent road deaths were a second, quieter tragedy, one that better public communication about risk could have helped prevent.

## Replication Materials

All code and data processing scripts are available in the [blog's GitHub repository](https://github.com/mjjohns1/nothing-so-practical). The analysis uses FARS microdata from NHTSA (1996-2004) and CausalPy for the Bayesian interrupted time series models. The original paper is "Dread Risk, September 11, and Fatal Traffic Accidents" (*Psychological Science*, 2004).
