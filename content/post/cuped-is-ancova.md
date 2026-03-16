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

Anyone running AB tests in industry knows the challenges. Detecting small but meaningful effects is difficult and time consuming. You can run the experiment longer, recruit more users, or accept that some effects will go undetected. None of those options appealing when you're running lots of tests and your stakeholders wanted the results yesterday.

Deng et al. (2013) proposed CUPED (Controlled-experiment Using Pre-Experiment Data) to address this problem. The idea is to collect outcome data on users *before* the experiment starts and statistically adjust for those pre-experiment observations when analyzing results. The pre-treatment version of the outcome captures user-specific variance that adds noise to your estimates. Removing it lets you detect a smaller effect with the same sample size, or the same effect with a smaller sample size. Let's see how this works in practice.

#### A Working Example

Imagine we are running an experiment to test if an updated page layout increases the use of a search feature on our platform. We end up randomly assigning about 10,000 users to either treatment (new layout) or control (old layout). Users vary in how likely they are to use the search function. Some search more while others users search less, on average. This natural variation acts as noise when estimating the treatment effect.

Most of those 10,000 users used the search feature at least once before the experiment started, and we have their prior usage rate. The average pre-experiment search rate across the users is 17%. For each user, CUPED subtracts that average, $\bar{X}$, from their individual pre-experiment search rate, $X_i$, adjusts this difference by a weight $\theta$, and then subtracts the result from the rate observed during the experiment, $Y_i$. The result is a version of the outcome, $Y_i^{adj}$, free of individual differences in search tendencies. Putting it all together, we get the following adjustment formula:

$$Y_i^{adj} = Y_i - \theta (X_i - \bar{X})$$

The coefficient $\theta$ represents how strongly the pre-experiment search behavior correlates with behavior measured during the experiment. A user with a search rate 10 percentage points higher than average before the experiment will tend to search more during, for reasons unrelated to the treatment. The adjustment subtracts that expected excess, leaving behind variation attributable to the treatment.

To estimate $\theta$, we need to calculate the covariance between the pre-experiment and in-experiment search rates, and divide by the variance of the pre-experiment metric.

$$\theta = \frac{\text{Cov}(Y, X)}{\text{Var}(X)}$$

Astute readers might recognize this as the slope coefficient for a simple linear regression of $Y$ on $X$. In our hypothetical experiment, $\hat{\theta}$ = 0.60. A user with a pre-experiment search rate of 27% (10 points above the 17% average) gets their observed rate adjusted downward by 0.60 $\times$ 10 = 6.0 percentage points. A user at 7% (10 points below average) gets adjusted upward by 6.0 points. Users at the mean get no adjustment.

After performing the adjustment, we can estimate the treatment effect as a simple difference in means of the new outcome values, $Y_i^{adj}$.

The variance reduction depends on the correlation between the pre-experiment and in-experiment metrics. In our data, pre-experiment and in-experiment search rates are positively correlated, $\rho$ = 0.69. The variance of the adjusted outcome is:

$$\text{Var}(Y^{adj}) = \text{Var}(Y) \times (1 - \rho^2) = 71.7 \times 0.52 = 37.5$$

That's a 48% reduction in the variance of $Y$. The standard error of the treatment effect, $\tau$, drops from 0.17 to 0.12, a 28% reduction. The sampling distribution of $\hat{\tau}$ (the estimated treatment effect) gets visibly tighter.

![Sampling distribution of the treatment effect estimate](/img/posts/cuped/tx_effect_distributions.svg)
*The adjusted estimate (blue) is more precise, concentrating probability mass closer to the true effect. In practice, this means you'd need roughly half as many users to achieve the same statistical power.*

The relationship between $\rho$ and variance remaining follows a curve that accelerates as $\rho$ increases.

![Variance reduction as a function of correlation](/img/posts/cuped/variance_reduction.svg)

### CUPED in Context

Anyone trained in the design and analysis of experiments will likely recognize the technique CUPED is employing. Analysis of covariance (ANCOVA) has traditionally been used to adjust for covariates to produce more precise treatment estimates (Keppel, 1991). The ideal covariate has a strong linear relationship with the outcome and no relationship with the treatment. Random assignment guarantees the second condition for *all* pre-treatment variables: however, the optimal covariate is almost always the pre-treatment version of the outcome.

Instead of first adjusting each user's outcome and then comparing group means, ANCOVA fits a single regression model that estimates the treatment effect and the covariate adjustment simultaneously.[^1]

$$y_i = \mu + \tau T_i + \beta X_i + \epsilon_i$$

The treatment effect estimate is $\tau$. The coefficient $\beta$ plays the same role as $\theta$ in CUPED. It accounts for the fact that users with higher pre-experiment search rates tend to have higher in-experiment rates. By explaining that variation, the model reduces residual error and produces a more precise estimate of $\tau$.

Here's what the two methods look like side-by-side using simulated data from our hypothetical experiment.

{{< figure src="/img/posts/cuped/cuped_vs_ancova.svg" caption="<strong>Left:</strong> ANCOVA fits parallel regression lines. The treatment effect is the constant vertical gap. <strong>Right:</strong> CUPED removes the pre-experiment relationship, tightening the scatter and leaving two flat group means. Both arrive at the same treatment effect of 3.0." class="img-center" >}}

The treatment effect estimates are functionally equivalent.[^2] Our ANCOVA model produces $\hat{\tau}$ = 3.03 with $\hat{\beta}$ = 0.61. CUPED produces $\hat{\tau}$ = 3.03 with $\hat{\theta}$ = 0.60.

The primary difference between methods appears to be mechanical. CUPED multiplies $\theta$ by the mean-centered pre-experiment outcome, which zeros out the slopes and collapses the parallel lines into flat group means. The methodological distinction is that ANCOVA estimates $\beta$ simultaneously with $\tau$, while CUPED estimates $\theta$ in a prior step, treating it as a known constant during inference.[^3]

Under random assignment, a user's pre-experiment search behavior is independent of their assigned condition. Estimating the covariate coefficient from experiment data versus historical data converges to the same answer as sample size increases. Both methods achieve a variance reduction of $\text{Var}(Y) \times (1 - \rho^2)$.

#### The Case for CUPED

The main argument for using CUPED over ANCOVA and regression adjustment is the concern that assumptions are often violated in real data. In motivating CUPED, Deng et al. state:

>Moreover, the technique should preferably not be based on any parametric model because model assumptions tend to be unreliable and a model that works for one metric does not necessarily work for another.

>However, the linear model makes strong assumptions that are usually not satisfied in practice, i.e., the conditional expectation of the outcome metric is linear in the treatment assignment and covariates. In addition, it also requires all residuals to have a common variance.

Whether these are actually "strong" assumptions is open to debate. In their classic book on regression modeling, Gelman and Hill (2006) point out that not all assumptions are created equal. They rank them as follows:

1. Validity
2. **Additivity and linearity**
3. Independence of errors
4. **Equal variance of errors**
5. Normality of errors

The linearity assumption is concerned with the model coefficients, not the shape of the relationship between $X$ and $Y$. When a straight line is inappropriate, we can add polynomial terms without violating linearity. The same goes for covariate adjustment in experiments. The real issue is whether the regression slopes of $Y$ on $X$ in treatment and control are parallel. Non-parallel slopes mean the treatment effect varies with $X$ (e.g., the new layout helps light searchers more than heavy ones). Under randomization, both ANCOVA and CUPED still produce consistent estimates of the *average* treatment effect even when slopes differ. What you lose is efficiency and the ability to interpret $\tau$ as a constant effect for all users. An interaction term would capture the heterogeneity and recover additional variance reduction.

The equal variance assumption (aka, homoscedasticity) sits near the bottom of the list. This assumption is weaker than most econometricians would have you believe. In large samples, regression estimates are generally robust to unequal error variance. Robust standard errors have been available for decades to deal with this problem. While they can be difficult to use in some situations, robust methods are perfectly suitable for a simple treatment model with only two variables.

CUPED does have a practical advantage worth noting. The two-step structure makes it natural to pre-compute $\theta$ outside the experiment. If a platform has historical paired observations (e.g., user behavior in two consecutive weeks before the experiment), it can estimate the covariance structure once and reuse it across experiments. You could technically do the same with regression, pre-computing $\beta$ from historical data and plugging it in. CUPED's formulation makes this separation obvious, which has engineering value for platforms running hundreds of experiments. The statistical result is identical either way.

### What to Make of CUPED

On the surface, CUPED appears to be a novel method for improving statistical power when analyzing online experiments. Once you peer below the surface, the novelty is less obvious. Both CUPED and ANCOVA can be used to reduce residual variance. Both achieve the same amount of variance reduction because they are governed by the same correlation. The differences are largely mechanical. CUPED pre-computes a single adjustment coefficient and applies it before comparing group means. ANCOVA estimates everything in one model. In large samples, the methods will converge.

Recognizing CUPED as a reformulation of regression adjustment opens up possibilities that the formula alone obscures. If there are multiple variables that predict the outcome (prior click rate, session length, user tenure) you can use them all. Variance reduction depends on how much additional outcome variance each predictor explains beyond what the others already capture. With CUPED, incorporating multiple covariates would require constructing a composite score, which amounts to fitting a regression anyway. Non-linear relationships between pre-experiment and in-experiment metrics could be handled with a squared term. If you suspect the layout change works differently for new users versus veteran users, include an interaction term. None of these require exotic techniques. They are standard regression tools.

Treating CUPED as a standalone formula, rather than a special case of regression, leaves flexibility on the table. None of this diminishes the value of CUPED. The idea brought covariate adjustment into the online experimentation mainstream at a time when many platforms still analyzed raw means. The next step is recognizing that you've been doing regression all along.

##### References

Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013). Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data. *Proceedings of the Sixth ACM International Conference on Web Search and Data Mining*, 123–132.

Gelman, A. & Hill, J. (2006). *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge University Press.

Keppel, G. (1991). *Design and analysis: A researcher's handbook* (3rd ed.). Prentice-Hall, Inc.

[^1]: I'm using ANCOVA and regression interchangeably to emphasize the fact that all you're doing is fitting a linear model to estimate a treatment effect, $\tau$, while controlling for a covariate, $X$. ANCOVA is typically used when the treatment variable is categorical. Regression can handle categorical treatment variables, as well as continuous treatments. Thus, ANCOVA can be seen as a special case of regression.

[^2]: Technically, they are not algebraically identical in finite samples. CUPED uses the marginal slope $θ = Cov(Y,X)/Var(X)$; ANCOVA technically estimates a partial regression coefficient. These converge asymptotically under random assignment but can differ in any given sample.

[^3]: Because CUPED ignores estimation uncertainty in $\theta$, its standard errors will tend to be optimistic (too small). ANCOVA accounts for this through joint estimation of $\beta$ and $\tau$. The difference will be negligible in large samples but matters for smaller experiments.
