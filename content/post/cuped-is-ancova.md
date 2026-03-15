---
title:       "Old Wine in a New Bottle: CUPED"
subtitle:    "COMING SOON"
description: "CUPED has become a popular feature in online experimentation platforms. You could have just used ANCOVA"
date:        2026-03-09
author:      "MJ"
image:       ""
tags:        ["statistics"]
categories:  []
draft:       FALSE
---

## What is CUPED?

Anyone running AB tests in industry is familiar with the challenges. Detecting small but important effects is difficult and time consuming. You can run the experiment longer, recruit more users, or accept that some real effects will go undetected. None of those options are appealing when you're running lots of experiments and your stakeholders wanted the results yesterday.

Deng et al. (2013) proposed CUPED (Controlled-experiment Using Pre-Experiment Data) to address these issues. The idea is to collect outcome data on users before the experiment starts and statistically adjust for those pre-experiment observations when analyzing the results. The pre-treatment versoin of the outcome contains information about user-specific variance. This variance adds noise to your estimates. Removing it allows you to detect a smaller effect with the same sample size, or the same effect with a smaller sample size.

### How Does it Work?

Imagine you plan to run an experiment to test if an updated page layout increases use of a (neglected) search feature. You randomly assign 50,000 users between treatment (new layout) and control (old layout). Users vary in how often they need to search. Heavy users tend to search less while casual users search more. This natural variation is a source of noise. It has nothing to do with whether the new layout is effective.

Most of those 50,000 used the search feature at least once before the experiment started. You have their usage rate from the prior year. Past search use is a moderatly strong predictor of future use. To apply CUPED, average the pre-experiment search rate (SR) across all users. Let's say it comes out to 32%. For each user, subtract the average from their actual pre-experiment rate, weight it by the strength of the relationship between the pre-experiment rate and experiment rate, finally subtracting that from the observed search rate in the experiment.

**Adjusted SR = In-experiment SR − $θ$ × (Pre-experiment SR − 32%)**

The coefficient $θ$ captures how strongly a user's pre-experiment behavior predicts their in-experiment behavior. A user who used search 10 percentage points more than average before the experiment would also tend to click more during, for reasons having nothing to do with the treatment. The adjustment subtracts that expected excess, leaving behind variation that is attributable to the treatment itself.

To make it concrete, suppose we estimate $θ$ = 0.6 (more on where this number comes from shortly). A user with a pre-experiment SR of 42% has their observed SR adjusted downward by 0.6 × (.42 - .32) = 6 percentage *points*. A user with a pre-experiment SR of 22%, 10 points below average, gets their SR adjusted upward by 6 points. Users right at the average get no adjustment at all.

After this adjustment, you estimate the treatment effect as a simple difference in adjusted SR between treatment and control.

To estimate $θ$ we need to calculate the covariance between the pre-experiment SR and in-experiment SR, and divide that by the variance of the pre-experiment metric. You might recogonize this values as the slope coefficient in a simple linear regression model. In fact, the easiest way to calculate $θ$ to fit a model regressing the SR observed in the experiment onto the pre-experiment SR.

How much variance does this remove? It depends entirely on the correlation between the pre-experiment and experiment metric. With a correlation of 0.7 the variance of the adjusted outcome is:

**Var(adjusted) = Var(observed) × (1 − 0.7²) = Var(observed) × 0.51**

In other words, the variance of the outcome is nearly halfed. The standard error of your treatment effect estimate, which is proportional to the square root of that variance, shrinks by about 29%. In practice this means you'd need roughly half as many users to achieve the same statistical power.

If the correlation were higher, say 0.9, the variance reduction would be even more dramatic: 1 − 0.9² = 19% of the original variance, an 81% reduction. If the correlation were lower, say 0.5, you'd reduce variance by only 25%. The pre-experiment metric only helps you to the extent that it actually predicts the experiment outcome.

## CUPED in Context

Anyone with formal training in the design and analysis of experiments will probably recognize this technique. You typically learn about analysis of covariance (ANCOVA) and how it can be used to produce more precise treatment esitimates. For ANCOVA, the ideal covariate has a strong linear relationship with the outcome and no relationship with the treatment. Because randomization makes all background variables independent of the treatment, there are often many potential covariates. However, the *optimal* covariate is the pre-treatment version of the outcome, by definition.


CUPED bares a striking resemblance to ANCOVA. Instead of first adjusting each user's outcome and then comparing group means, you fit a single regression model that estimates the treatment effect and the pre-experiment adjustment simultaneously:

**SR = α + τ × Treatment + β × Pre-experiment SR + error**

The treatment effect estimate is $τ$. The coefficient $β$ plays the same role as $θ$ in CUPED. It accounts for the fact that users with higher pre-experiment search rates will tend to have higher in-experiment search rates. By explaining that variation, it reduces the residual error in the model. Lower residual error means a more precise estimate of $τ$.

Here's what the two methods look like side-by-side.

![ANCOVA vs CUPED: same data, same treatment effect, different approach](/img/posts/cuped/cuped_vs_ancova.png)
*Left: ANCOVA fits parallel regression lines — the treatment effect is the constant vertical gap. Right: CUPED removes the pre-experiment relationship entirely, tightening the scatter and leaving two flat group means. Both arrive at the same estimate.*

The treatment estimates are the exactly same (3). The main difference is that CUPED multiplies $θ$ by the mean-centered version of the pre-experiment outcome. This has the effect of zeroing out the slopes. The notable methodological distinction is that ANCOVA estimates $β$ simultaneously while CUPED estimates $θ$ separately, in a prior step. In practice this means that $θ$ is fixed before you ever estimate the treatment effect. It's treated as a known constant during inference, not an estimated quantity.

Under random assignment, a user's pre-experiment behavior is independent of assigned condition, so estimating $β$ from experiment data versus pre-experiment data converges to the same answer. Both methods achieve the same variance reduction of

$$Var(Y) × (1 − ρ²)$$

There is one potential advantage to using CUPED. Because $θ$ only requires knowing how the pre- and in-experiment metrics covary on average, you can estimate it from aggregate historical statistics rather than fitting a model on participants. In large tech platforms where data pipelines are complex and experiment infrastructure is centralized, being able to pre-compute $θ$ once has some potential engineering value. But the statistical impact is identical.

The main argument against using ANCOVA (and regression) is the fact that the assumptions of parametric models are often violated in real data.

>Moreover, the technique should preferably not be based on any parametric model because model assumptions tend to be unreliable and a model that works for one metric does not necessarily work for another.

>However, the linear model makes strong assumptions that are usually not satisfied in practice, i.e., the conditional expectation of the outcome metric is linear in the treatment assignment and covariates. In addition, it also requires all residuals to have a common variance.

Whether these are "strong" assumptions is a constant topic of debate. Gelman and Hill (2006) argue that not all assumptions are created equal. They rank them as follows:

1. Validity: The data should map to the research question.
2. Additivity and linearity: The most important mathematical assumption. The deterministic component is a linear function of the separate predictors.
3. Independence of errors:
4. Equal variance of errors
5. Normality of errors


The linearity assumption is about whether it is valid to describe the relationship between a covariate the outcome using a straight line. If not, a simple solution is to apply a transformation to the covariate. Polynomial regeression is a common an example of this technique. The assumption that residuals have common variance is actually a weak assumption, despite what econometricians would have you believe. Most methods are robust to violations of homoscedasticity. If you are worried about it, you can just use a robust method, like the sandwich estimator.

The point is, solutions to these problems already exist. We didn't need an entirely new method to deal with them.

## What You Gain by Recognizing the Connection

Once you see CUPED as regression adjustment, the entire toolkit of regression becomes available.

Why use only one pre-period metric? If you have multiple variables that predict the outcome — prior click rate, prior session length, user tenure — include them all. Variance reduction depends on how much additional outcome variance each new predictor explains beyond what the others already captured. In the search example, adding session length as a second covariate might push your correlation from 0.7 to 0.8, cutting residual variance to 36% of the original instead of 51%.

What if the relationship between the pre-period metric and the experiment outcome isn't linear? Heavy users and light users might respond differently. Add a squared term, transform the variable, use a spline. Standard regression techniques apply directly. CUPED as a recipe doesn't tell you any of this. Regression thinking does.

Deng et al. warn against using post-treatment data as covariates, and they're right to. If your covariate is affected by the treatment, adjusting for it can absorb part of the treatment effect you're trying to measure, biasing your estimate in unpredictable ways. In the search example, adjusting for clicks during a "warm-up period" at the start of the experiment would be dangerous if the new ranking algorithm was already affecting behavior. This isn't a quirk of CUPED — it's a fundamental property of regression adjustment. Pre-treatment covariates are safe because treatment can't have caused them. Once you understand the method as regression, this assumption is obvious and easy to check.

## What to Make of CUPED

For data scientists and engineers who weren't trained in experimental methods, the paper provides an accessible entry point into a powerful and underused technique. If CUPED is the method that finally convinced your organization to use pre-treatment covariates, then CUPED did its job. But the underlying statistical idea is not new. Covariance adjustment has been standard practice in experimental design since Fisher's work in the 1920s. The statistical research community has been working on the problem of detecting small effects with limited resources for a century. The answers are in the literature.

Recognizing that CUPED is regression adjustment isn't pedantry. It's the difference between knowing a recipe and understanding why it works. A researcher who understands regression adjustment can handle novel situations that CUPED can't. A data scientist who only knows CUPED must wait for the next paper.

##### References

Gelman, A. & Hill, J. (2006) *Data Analysis Using Regression and Multilevel/Hierarchical Models*