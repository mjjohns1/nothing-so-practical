---
title:       "CUPED is ANOVA"
subtitle:    "COMING SOON"
description: "What your statistics book told you"
date:        2026-03-09
author:      "MJ"
image:       ""
tags:        ["statistics"]
categories:  []
draft:       true
---

## What is CUPED?

In 2013, Deng et al. proposed a method for improving the sensitivity of online experiments. CUPED, which stands for Controlled-experiment Using Pre-Experiment Data, addressed a problem familiar to anyone running A/B tests in industry. Even with millions of users, detecting small treatment effects is difficult and time consuming. You can run the experiment longer, recruit more users, or accept that some real effects will go undetected. None of those options are appealing when you're running thousands of experiments a year and trying to move fast.

The idea behind CUPED is simple. Collect outcome data on users before the experiment starts. When analyzing the results, statistically adjust for those pre-experiment observations. Random assignment ensures the pre-treatment version of the outcome is unrelated to treatment assignment, so the adjustment doesn't bias your estimate of the treatment effect. What it does do is reduce the noise in your estimates, letting you detect smaller effects with the same sample size.

The results were impressive. Deng et al. found CUPED reduced variance by roughly 50 percent in practice, meaning experiments could achieve the same power with half the users or half the duration. For a company running thousands of experiments annually, this is a substantial win.

### How Does it Work?

Say you're a data scientist at a search company running an experiment on a new ranking algorithm. Your outcome metric is click-through rate — the share of searches where the user clicked at least one result. You have 10,000 users split evenly between treatment and control.

The challenge is that users vary enormously in how often they click. Heavy searchers click constantly. Casual users barely engage. This user-to-user variation is noise from the perspective of your experiment. It has nothing to do with whether your new ranking algorithm works, but it inflates the uncertainty in your estimate of the treatment effect.

Here's the key insight. Most of those 10,000 users were using your search product before the experiment started. You have their click-through rates from the prior month. And it turns out that a user's click-through rate before the experiment is a strong predictor of their click-through rate during it — a correlation of around 0.7 is typical for this kind of metric. CUPED uses that pre-experiment behavior to filter out the noise that was always going to be there regardless of treatment.

The adjustment works like this. Suppose the average pre-experiment click-through rate across all users is 32%. For each user, you compute an adjusted outcome:

**Adjusted CTR = Observed CTR − θ × (Pre-experiment CTR − 32%)**

The coefficient θ captures how strongly a user's pre-experiment behavior predicts their in-experiment behavior. A user who clicked 10 percentage points more than average before the experiment would also tend to click more during it, for reasons having nothing to do with the treatment. The adjustment subtracts that expected excess, leaving behind variation that is more plausibly due to the treatment itself.

To make this concrete: suppose θ works out to 0.6 (more on where this number comes from shortly). A user with a pre-experiment CTR of 42% — 10 points above the 32% average — gets their observed CTR adjusted downward by 0.6 × 10% = 6 percentage points. A user with a pre-experiment CTR of 22% — 10 points below average — gets their CTR adjusted upward by 6 points. Users right at the average get no adjustment at all.

After this adjustment, you estimate the treatment effect as a simple difference in adjusted CTR between treatment and control.

Where does θ come from? It's estimated from the pre-experiment data alone, before the experiment is analyzed. Specifically, it's the number that minimizes the variance of the adjusted outcome — how much the adjusted CTRs spread around their mean. That optimal value turns out to be the ratio of how much the pre- and post-experiment metrics move together (their covariance) to how much the pre-experiment metric varies on its own (its variance). If you've ever fit a simple linear regression, this is the slope coefficient. More on that shortly.

How much variance does this remove? It depends entirely on the correlation between the pre- and post-experiment metric. With a correlation of 0.7 — realistic for the same metric measured a month apart — the variance of the adjusted outcome is:

**Var(adjusted) = Var(observed) × (1 − 0.7²) = Var(observed) × 0.51**

You've cut the variance of your outcome nearly in half. The standard error of your treatment effect estimate, which is proportional to the square root of that variance, shrinks by about 29%. In practice this means you'd need roughly half as many users to achieve the same statistical power. That's the 50 percent variance reduction Deng et al. reported.

If the correlation were higher — say 0.9, which you might see if users have very stable behavior — the variance reduction would be even more dramatic: 1 − 0.9² = 19% of the original variance, an 81% reduction. If the correlation were lower, say 0.5, you'd reduce variance by only 25%. The pre-experiment metric only helps you to the extent that it actually predicts the experiment outcome.

## How is CUPED Related to Other Methods?

At this point you might be wondering whether CUPED is really a new idea, or whether you've seen this before under a different name. You have.

Fisher introduced Analysis of Covariance (ANCOVA) in the 1920s and 1930s. He called pre-treatment variables "concomitant variables" and showed how to use them to improve precision in experiments. Cochran formalized the modern treatment in the 1950s. The technique appeared in Cochran and Cox's influential 1957 textbook on experimental design. ANCOVA has been standard practice in clinical trials, agricultural experiments, and psychology research for decades.

Here's what ANCOVA does in the search experiment above. Instead of first adjusting each user's outcome and then comparing group means, you fit a regression model that estimates the treatment effect and the pre-experiment adjustment simultaneously:

**CTR = α + τ × Treatment + β × Pre-experiment CTR + error**

The treatment effect estimate is τ. The coefficient β plays the same role as θ in CUPED — it accounts for the fact that users with higher pre-experiment click rates tend to have higher in-experiment click rates. By explaining that variation, it reduces the residual error in the model. Lower residual error means a more precise estimate of τ.

To put numbers on it: in your 10,000-user search experiment, suppose the unadjusted standard error on the treatment effect is 0.8 percentage points. Without adjustment, you'd need a true effect of about 1.6 points to detect it reliably (roughly two standard errors). With a pre-experiment covariate that has a 0.7 correlation with the outcome, the residual variance drops by 51%, the standard error shrinks to about 0.57 percentage points, and you can now reliably detect effects as small as 1.1 points. Same data, meaningfully more sensitive experiment.

![ANCOVA vs CUPED: same data, same treatment effect, different approach](/static/img/posts/cuped/cuped_vs_ancova.png)
*Left: ANCOVA fits parallel regression lines — the treatment effect is the constant vertical gap. Right: CUPED removes the pre-experiment relationship entirely, tightening the scatter and leaving two flat group means. Both arrive at the same estimate.*

## CUPED as Regression Adjustment

So what exactly is CUPED doing that ANCOVA isn't? Less than it might appear.

The optimal θ that Deng and colleagues derive is the OLS regression coefficient — the same number β that ANCOVA estimates. The adjusted outcome Ỹ that CUPED constructs is exactly what you'd get if you regressed the outcome on the pre-experiment metric and took the residuals. The control variates formulation in the paper is regression in different notation.

There is one real methodological distinction. ANCOVA estimates β simultaneously with the treatment effect, using the experimental data. CUPED estimates θ separately, in a prior step, from pre-experiment data. In practice this means that in CUPED, θ is fixed before you ever look at treatment versus control — it's treated as a known constant during inference, not an estimated quantity. In your search experiment, you'd estimate θ from the prior month of data, then apply it to the experiment. ANCOVA estimates β from the experiment data itself.

In large samples this distinction disappears. Under random assignment, a user's pre-experiment behavior is independent of which condition they're assigned to, so estimating β from experiment data versus pre-experiment data converges to the same answer. Both methods achieve the same variance reduction of Var(Y) × (1 − ρ²). The two approaches are equivalent in the limit.

There is also a narrow practical advantage to CUPED's separation. Because θ only requires knowing how the pre- and post-experiment metrics co-vary on average, you can estimate it from aggregate historical statistics rather than fitting a model on individual experimental subjects. In large tech platforms where data pipelines are complex and experiment infrastructure is centralized, being able to pre-compute θ once and apply it to many experiments has real engineering value — even if the statistical content is identical.

## What You Gain by Recognizing the Connection

Once you see CUPED as regression adjustment, the entire toolkit of regression becomes available.

Why use only one pre-period metric? If you have multiple variables that predict the outcome — prior click rate, prior session length, user tenure — include them all. Variance reduction depends on how much additional outcome variance each new predictor explains beyond what the others already captured. In the search example, adding session length as a second covariate might push your correlation from 0.7 to 0.8, cutting residual variance to 36% of the original instead of 51%.

What if the relationship between the pre-period metric and the experiment outcome isn't linear? Heavy users and light users might respond differently. Add a squared term, transform the variable, use a spline. Standard regression techniques apply directly. CUPED as a recipe doesn't tell you any of this. Regression thinking does.

Deng et al. warn against using post-treatment data as covariates, and they're right to. If your covariate is affected by the treatment, adjusting for it can absorb part of the treatment effect you're trying to measure, biasing your estimate in unpredictable ways. In the search example, adjusting for clicks during a "warm-up period" at the start of the experiment would be dangerous if the new ranking algorithm was already affecting behavior. This isn't a quirk of CUPED — it's a fundamental property of regression adjustment. Pre-treatment covariates are safe because treatment can't have caused them. Once you understand the method as regression, this assumption is obvious and easy to check.

## What to Make of CUPED

CUPED delivered real value. The 50 percent variance reduction is substantial. The practical guidance helps practitioners implement the method correctly. The empirical validation at Microsoft scale demonstrates it works in production systems. For data scientists and engineers who weren't trained in experimental statistics, the paper provides an accessible entry point into a powerful and underused technique. If CUPED is the method that finally convinced your organization to use pre-treatment covariates, then CUPED did its job.

But the underlying statistical idea is not new. Covariance adjustment has been standard practice in experimental design since Fisher's work in the 1920s. The statistical research community has been working on the problem of detecting small effects with limited resources for a century. The answers are in the literature.

Recognizing that CUPED is regression adjustment isn't pedantry. It's the difference between knowing a recipe and understanding why it works. A researcher who understands regression adjustment can handle novel situations that CUPED can't. A data scientist who only knows CUPED must wait for the next paper.
