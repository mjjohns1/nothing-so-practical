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

## What is CUPED?

Anyone running AB tests in industry knows the challenges. Detecting small but meaningful effects is difficult and time consuming. You can run the experiment longer, recruit more users, or accept that some effects will go undetected. None of those options appealing when you're running lots of tests and your stakeholders wanted the results yesterday.

Deng et al. (2013) proposed CUPED (Controlled-experiment Using Pre-Experiment Data) to address this problem. The idea is to collect outcome data on users *before* the experiment starts and statistically adjust for those pre-experiment observations when analyzing results. The pre-treatment version of the outcome captures user-specific variance that adds noise to your estimates. Removing it lets you detect a smaller effect with the same sample size, or the same effect with a smaller sample size. Let's see how this works in practice.

#### A Worked Example

Imagine you are running an experiment to test if an updated page layout increases the use of a search feature. You end up randomly assigning about 10,000 users to either treatment (new layout) or control (old layout). Users vary in how likely they are to use the search function. Some search more while others users search less, on average. This natural variation is acts as noise when estimating the treatment effect. It has nothing to do with whether the new layout works.

Most of those 10,000 users used the search feature at least once before the experiment started, and you have their prior usage rate. The average pre-experiment search rate across the users is 17%. For each user, CUPED subtracts that average, $\bar{X}$, from their individual pre-experiment rate, $X_i$, adjusts this difference by a weight $\theta$, and then subtracts the result from the search rate observed during the experiment, $Y_i$. The result is a version of the outcome, $Y_i^{adj}$, free of individual differences in search tendencies. Putting it all together, we get:

$$Y_i^{adj} = Y_i - \theta (X_i - \bar{X})$$

The coefficient $\theta$ represents how strongly the pre-experiment search behavior correlates with search behavior measured during the experiment. A user with a search rate 10 percentage points higher than average before the experiment will tend to search more during, for reasons unrelated to the treatment. The adjustment subtracts that expected excess, leaving behind variation attributable to the treatment.

To estimate $\theta$, we need to calculate the covariance between the pre-experiment and in-experiment search rates,  and divide by the variance of the pre-experiment metric.

$$\theta = \frac{\text{Cov}(Y, X)}{\text{Var}(X)}$$

Astute readers might recognize this as the slope coefficient in a simple linear regression of $Y$ on $X$. In our hypothetical experiment, $\hat{\theta}$ = 0.60. A user with a pre-experiment SR of 27% (10 points above the 17% average) gets their observed SR adjusted downward by 0.60 $\times$ 10 = 6.0 percentage points. A user at 7% (10 points below average) gets adjusted upward by 6.0 points. Users at the mean get no adjustment.

After adjusting, you estimate the treatment effect as a simple difference in means of the adjusted outcome values.

The variance reduction depends on the correlation between the pre-experiment and in-experiment metrics. In our data, pre-experiment and in-experiment search rates are positively correlated, $\rho = 0.69$. Users who searched more before the experiment tend to search more during it. The variance of the adjusted outcome is

$$\text{Var}(Y^{adj}) = \text{Var}(Y) \times (1 - \rho^2) = 71.7 \times 0.53 = 37.9$$

That's a 47% reduction in the variance of $Y$. The standard error of the treatment effect estimate drops from 0.17 to 0.12, a 29% reduction. The sampling distribution of $\hat{\tau}$ gets visibly tighter.

![Sampling distribution of the treatment effect estimate](/img/posts/cuped/tx_effect_distributions.svg)
*The adjusted estimate (blue) is more precise, concentrating probability mass closer to the true effect. In practice, this means you'd need roughly half as many users to achieve the same statistical power.*

The relationship between $\rho$ and variance remaining follows a curve that accelerates as $\rho$ increases.

![Variance reduction as a function of correlation](/img/posts/cuped/variance_reduction.svg)

### CUPED in Context

Anyone trained in experimental design will recognize the technique CUPED is employing. Analysis of covariance (ANCOVA) can also be used to adjust for covariates to produce more precise treatment estimates. The ideal covariate has a strong linear relationship with the outcome and no relationship with the treatment. Random assignment guarantees the second condition for all pre-treatment variables: however, the *optimal* covariate is almost always the pre-treatment version of the outcome.

Instead of first adjusting each user's outcome and then comparing group means, ANCOVA fits a single regression model that estimates the treatment effect and the covariate adjustment simultaneously.[^1]

$$y_i = \mu + \tau_i + \beta X_i + \epsilon_i$$

The treatment effect estimate is $\hat{\tau}$. The coefficient $\beta$ plays the same role as $\theta$ in CUPED. It accounts for the fact that users with higher pre-experiment search rates tend to have higher in-experiment rates. By explaining that variation, the model reduces residual error and produces a more precise estimate of $\tau$.

Here's what the two methods look like side-by-side in the simulated data.

{{< figure src="/img/posts/cuped/cuped_vs_ancova.svg" caption="<strong>Left:</strong> ANCOVA fits parallel regression lines. The treatment effect is the constant vertical gap. <strong>Right:</strong> CUPED removes the pre-experiment relationship, tightening the scatter and leaving two flat group means. Both arrive at the same treatment effect of 3.0." class="img-center" >}}

The treatment effect estimates are functionally equivalent.[^2] Our ANCOVA model produces $\hat{\tau}$ = 3.03 with $\hat{\beta}$ = 0.61. CUPED produces $\hat{\tau}$ = 3.03 with $\hat{\theta}$ = 0.60.

The primary difference between methods is mechanical. CUPED multiplies $\theta$ by the mean-centered pre-experiment outcome, which zeros out the slopes and collapses the parallel lines into flat group means. The methodological distinction is that ANCOVA estimates $\beta$ simultaneously with $\tau$, while CUPED estimates $\theta$ in a prior step, treating it as a known constant during inference. Note that because CUPED ignores estimation uncertainty in $\theta$, its standard errors will be optimistic (too small). ANCOVA accounts for this automatically through joint estimation. The difference is negligible in large samples but matters for smaller experiments.

Under random assignment, a user's pre-experiment search behavior is independent of their assigned condition. Estimating the covariate coefficient from experiment data versus historical data converges to the same answer as sample size increases. Both methods achieve a variance reduction of $\text{Var}(Y) \times (1 - \rho^2)$.

CUPED does have one potential advantage. Because $\theta$ only requires knowing how the pre- and in-experiment metrics covary on average, you can estimate it from aggregate historical statistics rather than fitting a model on experiment participants. For large tech platforms with complex data pipelines and centralized experiment infrastructure, pre-computing $\theta$ once has engineering value. But the statistical result is identical.

The main argument against ANCOVA appears to be that regression assumptions are often violated in real data. In setting the stage for CUPED, Deng et al. state:

>Moreover, the technique should preferably not be based on any parametric model because model assumptions tend to be unreliable and a model that works for one metric does not necessarily work for another.

>However, the linear model makes strong assumptions that are usually not satisfied in practice, i.e., the conditional expectation of the outcome metric is linear in the treatment assignment and covariates. In addition, it also requires all residuals to have a common variance.

Whether these are actually "strong" assumptions is open to debate. In their classic book on regression, Gelman and Hill (2006) rank the assumptions as follows:

1. **Validity**
2. **Additivity and linearity**
3. **Independence of errors**
4. **Equal variance of errors**
5. **Normality of errors**

The linearity assumption asks whether a straight line adequately describes the relationship between the covariate and the outcome. If not, you can transform the covariate. Polynomial terms and splines are standard tools freely availble to all. The equal variance assumption is weaker than most econometricians would have you believe. In large samples, OLS estimates are generally robust under heteroscedasticity. But if you're worried about inference then robust standard errors have been available for decades.

### What to Make of CUPED

Once you see CUPED as a reformulation of regression adjustment, the entire toolkit of regression becomes available.

Why use only one pre-period metric? If you have multiple variables that predict the outcome (prior click rate, session length, user tenure) include them all. Variance reduction depends on how much additional outcome variance each new predictor explains beyond what the others already capture. Adding session length as a second covariate might push $\rho$ from 0.69 to 0.80, cutting residual variance to 36% of the original instead of 53%.

What if the relationship between the pre-period metric and the outcome isn't linear? Heavy users and light users might respond differently. Add a squared term, transform the variable, use a spline. Standard regression techniques apply directly. CUPED as a recipe doesn't tell you any of this. Regression thinking does.

For data scientists and engineers who weren't trained in experimental methods, CUPED provides an accessible entry point into a powerful technique. If reading Deng et al. convinced your organization to adjust for pre-treatment covariates, it did the job. But the underlying idea is not new. Covariance adjustment has been standard practice in experimental design since Fisher's work in the 1930s. Applied researchers in various fields have been working on the problem of detecting small effects with limited resources for decades. You're not the first person to encounter this problem.

Recognizing that CUPED is a form of regression adjustment isn't a triival academic point. It's the difference between knowing a reciped and understanding why it works. You'll eventually encounter a situation that CUPED, as a fixed formula, cannot handle. Regression is a general and flexible modeling framework that gives you options. And that's a good thing.

##### References

Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013). Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data. *Proceedings of the Sixth ACM International Conference on Web Search and Data Mining*, 123–132.

Gelman, A. & Hill, J. (2006). *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge University Press.

[^1]: I'm using ANCOVA and regression interchangeably to emphasize the fact that all you're doing is fitting a linear model to estimate a treatment effect, $\tau$, while controlling for a covariate, $X$. ANCOVA is typically used when the treatment variable is categorical. Regression can handle categorical treatment variables, as well as continuous treatments. Thus, ANCOVA can be seen as a special case of regression.

[^2]: Technically, they are not algebraically identical in finite samples. CUPED uses the marginal slope $θ = Cov(Y,X)/Var(X)$; ANCOVA technically estimates a partial regression coefficient. These converge asymptotically under random assignment but can differ in any given sample.
