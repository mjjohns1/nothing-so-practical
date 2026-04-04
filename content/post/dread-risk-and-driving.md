---
title:       "Dread Risk and Driving"
subtitle:    ""
description: ""
date:        2026-04-03T10:05:01-04:00
author:      ""
image:       ""
tags:        []
categories:  []
draft:       true
---

During the Post-period (2001-10-01 00:00:00 to 2001-12-01 00:00:00), the response variable had an average value of approx. 3405.33. By contrast, in the absence of an intervention, we would have expected an average response of 3287.69. The 95% interval of this counterfactual prediction is [3269.99, 3305.25]. Subtracting this prediction from the observed response yields an estimate of the causal effect the intervention had on the response variable. This effect is 117.64 with a 95% interval of [100.08, 135.34].

Summing up the individual data points during the Post-period, the response variable had an overall value of 10216.00. By contrast, had the intervention not taken place, we would have expected a sum of 9863.07. The 95% interval of this prediction is [9809.98, 9915.76].

The 95% HDI of the effect [100.08, 135.34] does not include zero. The posterior probability of an increase is 1.000. Relative to the counterfactual, the effect represents a 3.58% change (95% HDI [3.00%, 4.11%]).

This analysis assumes that the relationship between the time-based predictors and the response observed during the pre-intervention period remains stable throughout the post-intervention period. If the formula includes external covariates, it further assumes they were not themselves affected by the intervention. We recommend inspecting model fit, examining pre-intervention trends, and conducting sensitivity analyses (e.g., placebo tests) to support any causal conclusions drawn from this analysis.