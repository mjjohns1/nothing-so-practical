---
title:       "CUPED: Old Wine in a New Bottle?"
subtitle:    ""
description: "CUPED has become a popular feature in online experimentation platforms. Regression works fine too."
date:        2026-03-09
author:      "MJ"
image:       ""
tags:        ["statistics"]
categories:  []
draft:       FALSE
---

## CUPED: Old Wine in a New Bottle?

Running AB tests in industry comes with several challenges. Detecting small but meaningful effects is difficult and time consuming. You can run the experiment longer, recruit more users, or accept that some effects will go undetected. None of those options are appealing when you're running lots of tests and your stakeholders wanted the results yesterday.

Deng et al. (2013) proposed CUPED (Controlled-experiment Using Pre-Experiment Data) to address this problem. The idea is to collect outcome data on users *before* the experiment starts and statistically adjust for those pre-experiment observations when analyzing results. The pre-treatment version of the outcome captures user-specific variance that adds noise to your estimates. Removing it lets you detect a smaller effect with the same sample size, or the same effect with a smaller sample size. Let's see how this works in practice.

#### Yet Another Search Experiment

Imagine we are running an experiment to test if an updated page layout increases the use of a search widget on our platform. We randomly assign about 10,000 users to either treatment (new layout) or control (old layout). The outcome, $Y_i$, is each user's search rate, i.e., the proportion of visits during the experiment when they used the search widget. For example, a user who visited 20 times and searched on 6 of those occasions has a search rate of 30%. The covariate, $X_i$, is the same metric measured in the 6 months before the experiment started. Users vary in how likely they are to use the search widget. Some search on most of their visits while others rarely do. This natural variation acts as noise when estimating the treatment effect.

We only randomize users who used the search widget at least once in the preceding 6 month window. The average pre-experiment search rate among this group is 17%. For each user, CUPED subtracts that average, $\bar{X}$, from their individual pre-experiment search rate, $X_i$, adjusts this difference by a weight, $\theta$, and then subtracts the result from the search rate observed in the experiment, $Y_i$. The result is a version of the outcome, $Y_i^{adj}$, free of individual differences in search tendencies. Putting it all together, we get the following adjustment formula:

$$Y_i^{adj} = Y_i - \theta (X_i - \bar{X})$$

The coefficient $\theta$ represents how strongly the pre-experiment search behavior correlates with behavior measured during the experiment. A user with a search rate 10 percentage points higher than average before the experiment will tend to search more during, for reasons unrelated to the treatment. The adjustment subtracts that expected excess, leaving behind variation that is more about the treatment effect and less about individual differences.

To estimate $\theta$, we compute the covariance between the pre-experiment and in-experiment search rates, divided by the variance of the pre-experiment metric (using the full pooled sample).

$$\theta = \frac{\text{Cov}(Y, X)}{\text{Var}(X)}$$

Astute readers might recognize this as the slope coefficient for a simple linear regression of $Y$ on $X$. In our hypothetical experiment, $\hat{\theta}$ = 0.60. A user with a pre-experiment search rate of 27% (10 points above the 17% average) gets their observed rate adjusted downward by 0.60 $\times$ 10 = 6.0 percentage points. A user at 7% (10 points below average) gets adjusted upward by 6.0 points. Users at the mean get no adjustment.

After performing the adjustment, we can estimate the treatment effect as a simple difference in means of the new outcome values, $Y_i^{adj}$.

The amount of variance reduction depends on the correlation between the pre-experiment and in-experiment metrics. In our data, the two search rates are positively correlated, $\rho$ = 0.69. The variance of the adjusted outcome is:

$$\text{Var}(Y^{adj}) = \text{Var}(Y) \times (1 - \rho^2) = 71.7 \times 0.53 = 37.9$$

That's a 47% reduction in the variance of $Y$. Because the standard error is proportional to the square root of the variance, cutting variance in half doesn't cut the standard error in half. It drops by about 27% ($1 - \sqrt{0.53} \approx 0.27$). Still a meaningful gain. The sampling distribution of $\hat{\tau}$ gets visibly tighter.

![Sampling distribution of the treatment effect estimate](/img/posts/cuped/tx_effect_distributions.svg)
*The adjusted estimate (blue) is more precise, concentrating probability mass closer to the true effect.*

The relationship between $\rho$ and variance remaining follows a curve that accelerates as $\rho$ increases.

![Variance reduction as a function of correlation](/img/posts/cuped/variance_reduction.svg)

### CUPED in Context

Anyone trained in the design and analysis of experiments will likely recognize the technique CUPED is employing. Analysis of covariance (ANCOVA) has traditionally been used to adjust for covariates to produce more precise treatment estimates (Keppel, 1991). The ideal covariate has a strong linear relationship with the outcome and no relationship with the treatment. Random assignment guarantees the second condition for *all* pre-treatment variables; however, the optimal covariate is almost always the pre-treatment version of the outcome.

Instead of first adjusting each user's outcome and then comparing group means, ANCOVA fits a single regression model that estimates the treatment effect and the covariate adjustment simultaneously.[^1]

$$y_i = \mu + \tau T_i + \beta (X_i - \bar{X}) + \epsilon_i$$

The treatment effect estimate is $\tau$. The coefficient $\beta$ plays the same role as $\theta$ in CUPED. It accounts for the fact that users with higher (lower) pre-experiment search rates will tend to search more (less) during the experiment. By explaining that variation, the model reduces residual error and produces a more precise treatment estimate.

Here's what the two methods look like side-by-side using data from our hypothetical experiment.

{{< figure src="/img/posts/cuped/cuped_vs_ancova.svg" caption="<strong>Left:</strong> ANCOVA fits parallel regression lines. The treatment effect is the constant vertical gap, estimated at the grand mean. <strong>Right:</strong> CUPED removes the pre-experiment relationship, tightening the scatter and leaving two flat group means. Both arrive at the same treatment effect of 3.0." class="img-center" >}}

The treatment effect estimates are functionally equivalent.[^2] The ANCOVA model produces $\hat{\tau}$ = 3.03 with $\hat{\beta}$ = 0.61. CUPED produces $\hat{\tau}$ = 3.03 with $\hat{\theta}$ = 0.60.

The primary difference between methods appears to be mechanical. CUPED multiplies $\theta$ by the mean-centered pre-experiment outcome, which zeros out the slopes and collapses the parallel lines into flat group means. The methodological distinction is that ANCOVA estimates $\beta$ simultaneously with $\tau$, while CUPED estimates $\theta$ in a prior step, treating it as a known constant during inference.

Under random assignment, a user's pre-experiment search behavior is independent of their assigned condition. Estimating the covariate coefficient from experiment data versus historical data converges to the same answer as sample size increases. Both methods reduce the variance of the outcome to $\text{Var}(Y) \times (1 - \rho^2)$.

#### Those Pesky Assumptions

One argument for using CUPED over ANCOVA and regression adjustment is the concern that assumptions are often violated in real data. In motivating CUPED, Deng et al. state:

>Moreover, the technique should preferably not be based on any parametric model because model assumptions tend to be unreliable and a model that works for one metric does not necessarily work for another.

>However, the linear model makes strong assumptions that are usually not satisfied in practice, i.e., the conditional expectation of the outcome metric is linear in the treatment assignment and covariates. In addition, it also requires all residuals to have a common variance.

Whether these are actually "strong" assumptions is open to debate. In their classic book on regression modeling, Gelman and Hill (2006) point out that not all assumptions are created equal. They rank them as follows:

1. Validity
2. **Additivity and linearity**
3. Independence of errors
4. **Equal variance of errors**
5. Normality of errors

The linearity assumption is about bias. If the true relationship between $X$ and $Y$ is non-linear the estimate of $\tau$ will not suffer under randomization. Both ANCOVA and CUPED produce consistent estimates of the *average* treatment effect even when the $XY$ relationship is non-linear or when slopes differ across groups.[^3] What you lose is efficiency and the ability to interpret $\tau$ as a constant effect for all users.

Equality of variances is about the standard errors. Heteroscedasticity doesn't bias $\hat{\tau}$ but can make the default standard errors unreliable. In practice, this is a weaker assumption than most econometricians would have you believe. Robust standard errors have been available for decades. They are perfectly suitable for a simple treatment model with only two variables.

There is one situation where CUPED has an advantage. Think about what happens when you adjust each user's outcome and then compare group means. The CUPED treatment effect equals the raw difference in means minus a correction for any chance imbalance in pre-experiment search rates between groups. Randomization ensures this imbalance averages to zero, so the correction is just removing noise, keeping the estimator unbiased.

This means if you pre-compute $\theta$ from historical data (e.g., user behavior in two consecutive weeks before the experiment), no model assumptions are needed. You can even reuse the same $\theta$ across experiments (see Deng et al, 2023). But when $\theta$ is instead estimated from the experimental data, which is standard practice, it becomes a random variable that depends on outcomes, and the estimator collapses to ANCOVA.

Recall, however, that CUPED assumes $\theta$ is a constant. It ignores the uncertainty introduced by estimating it from data. ANCOVA accounts for uncertainty through joint estimation of $\beta$ and $\tau$. In large experiments with tens of thousands of participants, this difference is negligible. The sampling variance of $\theta$ shrinks faster than the experimental noise, so treating it as fixed is usually a harmless simplification.[^4] However, when the sample is small, which is arguably when variance reduction is *most* useful, CUPED's standard errors can be miscalibrated. Regression handles these cases naturally because it never pretends the covariate coefficient is known.

### What to Make of CUPED

Recognizing the overlap between CUPED and ANCOVA creates flexibility when you need to go beyond a simple adjustment formula. If the relationship between the covariate and outcome is non-linear, add polynomial or spline terms. If you suspect the treatment works differently for different types of users, add an interaction term. If multiple covariates are correlated with the outcome (prior click rate, session length, user tenure), include them all. Regression can handle it. With CUPED, incorporating multiple covariates requires constructing a composite score, which amounts to fitting a regression anyway.

CUPED works well in the environment it was designed for: large-scale online experiments with a single strong covariate and straightforward metrics. That describes a lot of AB tests but it doesn't describe them all. Regression has been doing this work for decades. It's more flexible, its assumptions are well understood, and it extends naturally when the simple case isn't simple enough. Knowing when the advantage of each method kicks in is useful. Defaulting to CUPED without recognizing that you really needed regression is not.

----
##### References

Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013). Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data. *Proceedings of the Sixth ACM International Conference on Web Search and Data Mining*, 123–132.

Deng, A., Hagar, L., Stevens, N., Xifara, T., Yuan, L., & Gandhi A., (2023). From Augmentation to Decomposition: A New Look at CUPED in 2023. arXiv. https://arxiv.org/abs/2312.02935

Gelman, A. & Hill, J. (2006). *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge University Press.

Keppel, G. (1991). *Design and analysis: A researcher's handbook* (3rd ed.). Prentice-Hall, Inc.

Lin, W. (2013). Agnostic Notes on Regression Adjustments to Experimental Data: Reexamining Freedman's Critique. *Annals of Applied Statistics*, 7(1), 295–318.

[^1]: I'm using ANCOVA and regression interchangeably to emphasize the fact that all you're doing is fitting a linear model to estimate a treatment effect, $\tau$, while controlling for a covariate, $X$. ANCOVA is used when the treatment variable is categorical. Regression can handle categorical treatment variables, as well as continuous treatments. ANCOVA can be seen as a special case of regression.

[^2]: The two estimators are not algebraically identical in finite samples. CUPED uses the marginal slope $\hat{\theta} = \text{Cov}(Y,X)/\text{Var}(X)$ pooled across groups, while ANCOVA estimates a partial slope $\hat{\beta}$ that conditions on treatment assignment.

[^3]: For a formal treatment of the heterogeneous treatment effect case, see Lin (2013), who shows that ANCOVA with treatment-covariate interactions is asymptotically at least as efficient as any linear adjustment under randomization alone.

[^4]: See Deng et al. (2023) for a detailed treatment of when and why treating $\theta$ as fixed is justified in large-sample settings.
