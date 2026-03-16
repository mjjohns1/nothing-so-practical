---
title:       "CUPED: Old Wine in a New Bottle?"
subtitle:    ""
description: "CUPED has become a popular feature in online experimentation platforms. You can just use regression."
date:        2026-03-09
author:      "MJ"
image:       ""
tags:        ["statistics"]
categories:  []
draft:       FALSE
---

## What is CUPED?

Anyone running AB tests in industry knows the challenges. Detecting small but meaningful effects is difficult and time consuming. You can run the experiment longer, recruit more users, or accept that some real effects will go undetected. None of those options appeal when you're running lots of experiments and your stakeholders wanted the results yesterday.

Deng et al. (2013) proposed CUPED (Controlled-experiment Using Pre-Experiment Data) to address this problem. The idea is to collect outcome data on users *before* the experiment starts and statistically adjust for those pre-experiment observations when analyzing results. The pre-treatment version of the outcome captures user-specific variance that adds noise to your estimates. Removing it lets you detect a smaller effect with the same sample size, or the same effect with a smaller sample size.

## A Worked Example

Suppose you're testing whether an updated page layout increases use of a search feature. You randomly assign 10,000 users, 5,000 to treatment (new layout) and 5,000 to control (old layout). Users vary in how often they search. Heavy users tend to search less while casual users search more. This natural variation is noise. It has nothing to do with whether the new layout works.

Most of those 10,000 users used the search feature before the experiment started, and you have their prior usage rate. The average pre-experiment search rate across all users is 17%. For each user, CUPED subtracts the average from their pre-experiment rate, weights the difference by a coefficient $\theta$, and subtracts the result from the observed in-experiment search rate.

$$Y_i^{adj} = Y_i - \theta \cdot (X_i - \bar{X})$$

<div style="background: #f7f7f7; border-left: 3px solid #ccc; padding: 12px 16px; margin: 1rem 0; font-size: 0.95em;">

**In words:** Take each user's in-experiment search rate ($Y_i$), then subtract an adjustment. The adjustment is $\theta$ (a weight capturing how predictive the pre-experiment metric is) times how far that user's pre-experiment rate ($X_i$) falls from the overall pre-experiment average ($\bar{X}$). Users above average get adjusted down. Users below average get adjusted up.
</div>

The coefficient $\theta$ captures how strongly pre-experiment behavior predicts in-experiment behavior. A user who searched 10 percentage points more than average before the experiment will tend to search more during it, for reasons unrelated to the treatment. The adjustment subtracts that expected excess, leaving behind variation attributable to the treatment.

### Where does $\theta$ come from?

To estimate $\theta$, calculate the covariance between the pre-experiment and in-experiment search rates and divide by the variance of the pre-experiment metric.

$$\theta = \frac{\text{Cov}(Y, X)}{\text{Var}(X)}$$

You might recognize this as the slope coefficient in a simple linear regression of $Y$ on $X$. In our simulation, $\hat{\theta}$ = 0.60. A user with a pre-experiment SR of 27% (10 points above the 17% average) gets their observed SR adjusted downward by 0.60 $\times$ 10 = 6.0 percentage points. A user at 7% (10 points below average) gets adjusted upward by 6.0 points. Users at the mean get no adjustment.

After adjusting, you estimate the treatment effect as a simple difference in adjusted means between treatment and control.

### How much does it help?

The variance reduction depends on the correlation between the pre-experiment and in-experiment metrics. In our data, pre-experiment and in-experiment search rates are positively correlated. Users who searched more before the experiment tend to search more during it.

![Pre-experiment vs in-experiment search rates](/img/posts/cuped/pre_post_covariation.svg)
*Each point is a user. The correlation ($\rho$ = 0.69) is the signal CUPED exploits.*

The variance of the adjusted outcome is

$$\text{Var}(Y^{adj}) = \text{Var}(Y) \times (1 - \rho^2) = 71.7 \times 0.53 = 37.9$$

That's a 47% reduction in variance. The standard error of the treatment effect estimate drops from 0.17 to 0.12, a 29% reduction. The sampling distribution of $\hat{\tau}$ gets visibly tighter.

![Sampling distribution of the treatment effect estimate](/img/posts/cuped/tx_effect_distributions.svg)
*Both distributions are centered on the same estimate ($\hat{\tau}$ = 3.0). The adjusted estimate (blue) is more precise, concentrating probability mass closer to the true effect. In practice, this means you'd need roughly half as many users to achieve the same statistical power.*

How much you gain depends entirely on the strength of the correlation. The relationship between $\rho$ and variance remaining follows a curve that accelerates as $\rho$ increases.

![Variance reduction as a function of correlation](/img/posts/cuped/variance_reduction.svg)
*At $\rho$ = 0.69, just over half the original variance remains. At $\rho$ = 0.9, only 19% remains. The pre-experiment metric only helps to the extent it predicts the in-experiment outcome.*

## CUPED is ANCOVA

Anyone trained in experimental design will recognize this technique. Analysis of covariance (ANCOVA) adjusts for covariates to produce more precise treatment estimates. The ideal covariate has a strong linear relationship with the outcome and no relationship with the treatment. Random assignment guarantees the second condition for all pre-treatment variables, but the *optimal* covariate is the pre-treatment version of the outcome, by definition.

Instead of first adjusting each user's outcome and then comparing group means, ANCOVA fits a single regression that estimates the treatment effect and the covariate adjustment simultaneously.

$$Y_i = \alpha + \tau \cdot T_i + \beta \cdot X_i + \epsilon_i$$

The treatment effect estimate is $\hat{\tau}$. The coefficient $\beta$ plays the same role as $\theta$ in CUPED. It accounts for the fact that users with higher pre-experiment search rates tend to have higher in-experiment rates. By explaining that variation, the model reduces residual error and produces a more precise estimate of $\tau$.

Here's what the two methods look like side-by-side on our simulated data.

![ANCOVA vs CUPED](/img/posts/cuped/cuped_vs_ancova.svg)
*Left: ANCOVA fits parallel regression lines. The treatment effect is the constant vertical gap. Right: CUPED removes the pre-experiment relationship, tightening the scatter and leaving two flat group means. Both arrive at $\hat{\tau}$ = 3.0.*

The treatment effect estimates are identical. Our ANCOVA regression gives $\hat{\tau}$ = 3.03 with $\hat{\beta}$ = 0.61. CUPED gives $\hat{\tau}$ = 3.03 with $\hat{\theta}$ = 0.60. Not a coincidence.

The main difference is mechanical. CUPED multiplies $\theta$ by the mean-centered pre-experiment outcome, which zeros out the slopes and collapses the parallel lines into flat group means. The methodological distinction is that ANCOVA estimates $\beta$ simultaneously with $\tau$, while CUPED estimates $\theta$ in a prior step, treating it as a known constant during inference.

Under random assignment, a user's pre-experiment behavior is independent of their assigned condition. Estimating the covariate coefficient from experiment data versus historical data converges to the same answer. Both methods achieve a variance reduction of

$$\text{Var}(Y) \times (1 - \rho^2)$$

There is one practical advantage to CUPED. Because $\theta$ only requires knowing how the pre- and in-experiment metrics covary on average, you can estimate it from aggregate historical statistics rather than fitting a model on experiment participants. For large tech platforms with complex data pipelines and centralized experiment infrastructure, pre-computing $\theta$ once has engineering value. But the statistical result is identical.

## But What About the Assumptions?

The main argument against ANCOVA is that regression assumptions are violated in real data. From Deng et al.:

>Moreover, the technique should preferably not be based on any parametric model because model assumptions tend to be unreliable and a model that works for one metric does not necessarily work for another.

>However, the linear model makes strong assumptions that are usually not satisfied in practice, i.e., the conditional expectation of the outcome metric is linear in the treatment assignment and covariates. In addition, it also requires all residuals to have a common variance.

Whether these are "strong" assumptions depends on which assumptions you mean. Gelman and Hill (2006) rank regression assumptions by importance:

1. **Validity.** The data should map to the research question.
2. **Additivity and linearity.** The deterministic component is a linear function of the separate predictors. This is the most important mathematical assumption.
3. **Independence of errors.** Each observation provides independent information.
4. **Equal variance of errors.** The spread of residuals is constant across fitted values.
5. **Normality of errors.** The least important. Matters for small-sample inference, not for large experiments.

The linearity assumption asks whether a straight line adequately describes the relationship between the covariate and the outcome. If not, you can transform the covariate. Polynomial terms and splines are standard tools. The equal variance assumption is weaker than many believe. OLS estimates remain unbiased under heteroscedasticity. If you're worried about inference, use robust standard errors.

Solutions to these problems already exist. We didn't need an entirely new method to deal with them.

## What You Gain by Recognizing the Connection

Once you see CUPED as regression adjustment, the entire toolkit of regression becomes available.

Why use only one pre-period metric? If you have multiple variables that predict the outcome (prior click rate, session length, user tenure) include them all. Variance reduction depends on how much additional outcome variance each new predictor explains beyond what the others already capture. Adding session length as a second covariate might push $\rho$ from 0.69 to 0.80, cutting residual variance to 36% of the original instead of 53%.

What if the relationship between the pre-period metric and the outcome isn't linear? Heavy users and light users might respond differently. Add a squared term, transform the variable, use a spline. Standard regression techniques apply directly. CUPED as a recipe doesn't tell you any of this. Regression thinking does.

Deng et al. warn against using post-treatment data as covariates, and they're right. If your covariate is affected by the treatment, adjusting for it can absorb part of the effect you're trying to measure, biasing your estimate in unpredictable ways. Adjusting for clicks during a "warm-up period" at the start of the experiment would be dangerous if the new layout was already influencing behavior. This isn't a quirk of CUPED. It's a fundamental property of regression adjustment. Pre-treatment covariates are safe because treatment can't have caused them. Once you understand the method as regression, this constraint is obvious and easy to check.

## What to Make of CUPED

For data scientists and engineers who weren't trained in experimental methods, the Deng et al. paper provides an accessible entry point into a powerful technique. If CUPED convinced your organization to use pre-treatment covariates, it did its job. But the underlying idea is not new. Covariance adjustment has been standard practice in experimental design since Fisher's work in the 1920s. The statistical research community has been working on the problem of detecting small effects with limited resources for a century. The answers are in the literature.

Recognizing that CUPED is regression adjustment isn't pedantry. It's the difference between knowing a recipe and understanding why it works. A researcher who understands regression adjustment can handle situations that CUPED as a formula cannot. A data scientist who only knows CUPED must wait for the next paper.

##### References

Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013). Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data. *Proceedings of the Sixth ACM International Conference on Web Search and Data Mining*, 123–132.

Gelman, A. & Hill, J. (2006). *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge University Press.
