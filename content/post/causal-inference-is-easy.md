---
title:       "Causal Inference Is Easy"
subtitle:    "Don't be fooled by the math"
description: ' '
date:        2026-03-10
author:      "MJ"
image:       ""
tags:        ["causal inference"]
categories:  []
draft:       false
---


## Causal Inference is Easy

Causal inference seems to be having a moment. Why the sudden interest? The tech industry's belated realization that correlation really doesn't equal causation, no matter how big the data, could have something to do with it. It might also be that we've collectively worked through all the easy prediction problems and now need to answer harder questions about why things happen. Certainly, some of it is just methodological fashion.

Whatever the reason, available methods now make it possible to go beyond the mere association of machine learning. Of course, AB testing has been the workhorse of causal inference in the tech industry since the beginning of the dot-com era. Randomized experiments work well for identifying the best landing page design, or figuring out which creative drives the most site traffic. Determining if an out-of-home marketing campaign was cost effective, or if a new customer retention strategy increased lifetime value is not so straightforward.

{{< figure src="/img/posts/causal-inference/linkedin_causal_inference.png" alt="Important evidence of causal inference having a moment" width="67%" class="img-center" >}}

Increasingly, the causal questions that need answering can't be handled with randomized experiments in closed-loop systems. We want to know not just if it worked, but for whom and under what circumstances. Contemporary causal inference frameworks come into their own when experimentation isn’t possible. Pearl's structural approach, based on directed acyclic graphs (DAG), and Rubin’s potential outcomes framework, derived from statistical theory, provide principled approaches for getting to causation without the need to randomize. Recognizing their potential, scientific fields like epidemiology and econometrics were keen to adopt these methods starting back in the 1990s. This makes sense. Many of the focal questions in those disciplines can't be answered using experiments.

The key innovation of these approaches lies in their mathematical precision and rigor. Input a model of the data generating process or selection mechanisms, make some assumptions and out comes a set of equations that tell you what to do. Perfect for tech.

{{% notation-box %}}

**Sample notation from Potential Outcomes:**

$$\text{ATE} = E[Y_{1} - Y_{0}] =  E[E[Y_{1i}\mid D=1, X] - E[Y_{0i}\mid D=0, X]]$$
*where $Y_{1}$, $Y_{0}$ are potential outcomes, $D$ is treatment, and $X$ are confounders*

**Sample from DAG framework:**

$$P(Y \mid \text{do}(X)) = \sum_z P(Y \mid X, Z=z) \, P(Z=z)$$
*the adjustment formula for blocking backdoor paths through Z*

{{% /notation-box %}}

Looking at the notation, it’s easy to think that modern causal inference is a complicated math problem. But strip away the notation, graphical models and estimators, and you're left with one simple task: eliminating alternative explanations for what you observe. That’s it. That’s all you’re doing. Easy.

### Let’s go to the Beach

Take the apocryphal correlation between ice cream sales and shark attacks. Both tend to spike during the same months. If you didn't know better, you might conclude that ice cream causes shark attacks. Or perhaps shark attacks cause people to seek comfort in ice cream.

![Ice cream sales and shark attacks track together across three years](/img/posts/causal-inference/icecream-sharks.svg)

Neither is true. The relationship exists because of a third variable, warm weather. During summer, more people buy ice cream and more people go in the ocean, increasing the chance of shark encounters. Once you account for seasonality, the relationship between ice cream and sharks disappears.[^1]

This is what eliminating alternative explanations looks like in its simplest form. You observe a relationship, ice cream and shark attacks rise and fall together. You propose a causal story that shark attacks cause ice cream sales. Then you simply ask, what else could explain this pattern? Seasonal temperature changes provide a rival hypothesis that's more plausible. Rule out warm weather, and you've eliminated the alternative explanation. If the correlation persists, you might have something causal. If it vanishes, you probably don't.

Now consider the relationship between hormone replacement therapy (HRT) and heart disease in postmenopausal women. Observational studies in the 1980s and 90s consistently showed that women taking HRT had lower rates of heart disease. The relationship was strong and persistent across multiple studies. Researchers concluded that HRT protected against heart disease and doctors began prescribing it widely.
Then came the randomized trials. The Women's Health Initiative, a large-scale RCT published in the early 2000s, found the opposite: HRT increased the risk of heart disease. How could so many observational studies have been wrong?[^2]

Selection bias is the usual suspect. Women who chose to take HRT in the observational studies tended to be more health-conscious than women who didn't. They exercised more, ate better, and saw their doctors more regularly. These factors, and not HRT, explained the lower heart disease rates. The observational studies had failed to eliminate a crucial alternative explanation. Perhaps women taking HRT were simply different from the women who weren't.

The randomized trial eliminated this alternative by making the treatment independent of all background characteristics. Whether you got HRT or a placebo was determined by chance, not by health habits or socioeconomic status. <mark>This is actually what makes randomized experiments the gold standard: *it is the most effective method available for eliminating potential alternative explanations.*</mark>
At their core, the DAG and potential outcomes frameworks are systematic tools for determining how best to eliminate alternative explanations. Let’s examine how each approach accomplishes this task.

### Modern Causal Inference

#### Potential Outcomes

The potential outcomes framework starts with a simple observation. For any individual, we can only observe one reality at a time. A participant either takes HRT or she doesn't. We never get to see what would have happened to the same person under the alternative scenario.

Consider a study participant who took the treatment and did not develop heart disease. Was HRT protective? To answer that causally, we'd need to know what would have happened if she hadn't taken HRT. But that's impossible to observe. She cannot simultaneously take HRT and not take HRT.

In the potential outcomes framework, we formalize this situation by defining two potential outcomes for each individual $i$:

$$\begin{aligned}
Y_{1i} &= \text{the outcome if individual } i \text{ receives treatment} \\
Y_{0i} &= \text{the outcome if individual } i \text{ does not receive treatment}
\end{aligned}$$

The individual causal effect is $\tau_i = Y_{1i} - Y_{0i}$. The problem is that we can only ever observe one of these potential outcomes. If participant $i$ takes HRT ($X_i = 1$), we observe $Y_{1i}$ but not $Y_{0i}$. If she doesn't take HRT ($X_i = 0$), we observe $Y_{0i}$ but not $Y_{1i}$.

What we'd like to estimate is the average treatment effect (ATE):

$$\text{ATE} = E[Y_{1i} - Y_{0i}] = E[Y_{1i}] - E[Y_{0i}]$$

This is the average difference in potential outcomes in the population. The naive approach is to compare the average observed (sample) outcome among the treated with the average observed outcome among untreated individuals:

$$E[Y_i \mid X_i = 1] - E[Y_i \mid X_i = 0]$$

But this only equals the ATE if:

$$E[Y_{1i} \mid X_i = 1] = E[Y_{1i}] \quad \text{and} \quad E[Y_{0i} \mid X_i = 0] = E[Y_{0i}]$$

In other words, the naive mean difference is only valid if the potential outcomes are independent of treatment assignment.
For the HRT case, this doesn't hold. Women who chose HRT ($X_i = 1$) have different potential outcomes than women who didn't, even before they took HRT. More health-conscious women were more likely to take HRT. So $E[Y_{0i} \mid X_i = 1] \neq E[Y_{0i} \mid X_i = 0]$. Even if HRT had no effect, the treated group would have had better outcomes on average simply because they were healthier to begin with.

This is a classic selection effect. The difference in observed outcomes conflates the treatment effect with pre-existing differences in potential outcomes. The naive comparison has an alternative explanation. The groups were simply different to begin with.

The standard solution in non-experimental studies is the conditional independence assumption:

$$(Y_{0i}, Y_{1i}) \perp X_i \mid Z_i$$

This says that conditional on observed variables in $Z$ (i.e., health consciousness, education level, income, etc.), treatment assignment is not related to potential outcomes. In other words, among women with the same levels of health consciousness, educational attainment and income, whether they chose HRT is essentially random with respect to their potential outcomes.

With the conditional independence assumption we can identify the ATE by conditioning on $Z$:

$$\text{ATE} = E\!\left[E[Y_i \mid X_i = 1, Z_i] - E[Y_i \mid X_i = 0, Z_i]\right]$$

At their core, statistical methods like regression adjustment, propensity score matching and inverse probability weighting are all just different ways of estimating this conditional expectation.

Notice what this assumption is really saying: once you control for $Z$, there are no remaining alternative explanations for differences in outcomes. All the confounding originates from $Z$. Any factor that affects both treatment choice and outcomes is captured in your set of covariates.

{{< figure src="/img/posts/causal-inference/conditioning-on-z.svg" caption="<strong>Left:</strong> A naive comparison of treated and control groups suggests treated individuals have better outcomes. But this difference is driven by confounding: the confounder Z influences both who receives treatment and the outcome. <strong>Right:</strong> When we condition on Z, comparing treated and control units within the same level of Z, the apparent effect disappears. The outcome distributions are nearly identical within each stratum, revealing that the naive difference was entirely due to confounding." class="img-center" >}}

If health consciousness affects both HRT uptake and heart disease risk, but you don't measure it, or you measure it poorly, or it interacts with other variables in complex ways, then the assumption can fail. You haven't eliminated the alternative, you've just assumed it away.

All the assumptions are just formal statements about having eliminated alternative explanations. Unconfoundedness says you've eliminated selection bias. The stable unit treatment value assumption (SUTVA) says you've eliminated interference and hidden versions of treatment as an explanation. Common support says you've eliminated the problem of groups that are too different to be comparable. Each assumption corresponds to a specific alternative explanation that could undermine your causal claim. The equations formalize these assumptions and show what estimator to use. But the assumptions themselves are about alternative explanations, not about math.

The formal machinery – notation, estimators, asymptotic theory – can obscure a fundamental point. All you’re trying to do is eliminate alternative explanations for your treatment estimate. Unconfoundedness is just a mathematical statement that you've done so, conditional on $X$.

#### Directed Acyclic Graphs

The DAG framework makes the alternative explanations visually explicit by mapping out the causal structure. For the HRT example, a DAG encoding the confounding story might look like this:

![A simple DAG showing confounding through health consciousness](/img/posts/causal-inference/dag-simple.svg)

This graph says that health consciousness ($Z$) causes both HRT ($X$) uptake and heart disease risk ($Y$). There may or may not be a causal arrow from HRT to heart disease. That’s what we're trying to figure out.

Relationships between variables can flow along any path connecting two variables, not just along causal arrows. There's a path from HRT to heart disease that goes: HRT ← Health Consciousness → Heart Disease. Even if HRT has zero causal effect on heart disease (no direct arrow from HRT to Heart Disease), there will still be statistical association between them because they share a common cause.

This is a backdoor path in DAG terminology. Backdoors are non-causal paths from treatment to outcome that go through a common cause. They create spurious correlations and represent alternative explanations for the observed relationship. To identify the causal effect of HRT on heart disease, we need to block all backdoor paths while leaving the causal path open. The backdoor criterion gives us a formal rule for doing this.

A set of variables, $Z$, is sufficient to control for confounding if:

- No variable in $Z$ is caused by $X$ (we don't want to control for mediators or colliders)
- $Z$ blocks all backdoor paths from $X$ to $Y$

In the DAG, controlling for health consciousness satisfies the backdoor criterion. It blocks the only backdoor path (HRT ← Health Consciousness → Heart Disease). Once we condition on health consciousness, HRT and heart disease are considered to be d-separated (directionally separated). There's no path through which non-causal correlation can flow.

Formally, conditioning on $Z$ gives us:

$$P(Y \mid \text{do}(X)) = \sum_z P(Y \mid X, Z=z) \, P(Z=z)$$

where $\text{do}(X)$ represents an intervention that sets the value of HRT (1 = taking HRT; 0 = not taking HRT), making it independent of its causes. The right-hand side can be estimated using observational data if we've measured $Z$ and the backdoor criterion is satisfied.
However, the DAG only helps if you've specified it correctly. If there's a variable you haven't included in the graph, say genetic predisposition to both seeking preventive care and having good cardiovascular health, then you haven't actually blocked all the backdoor paths. You've just assumed they don't exist.

Drawing the DAG requires a thorough understanding of the data generating process. You need to know what causes treatment selection, what causes the outcome, what variables cause both, what variables are caused by both, just to name a few. The graphical framework makes your assumptions explicit and provides rules for determining what you need to control for. But it doesn't tell you whether your graph is right. That requires understanding the domain.

Suppose income affects health consciousness, and income also independently affects heart disease risk (through stress, diet, healthcare access). Now your DAG looks like:

![A more complex DAG with multiple confounding paths](/img/posts/causal-inference/dag-income.svg)

Now there are two backdoor paths:

- $X \leftarrow Z \rightarrow Y$
- $X \leftarrow Z \leftarrow \text{Income} \rightarrow Y$

To block both paths, you could control for health consciousness alone (which also blocks the path through income), or you could control for income alone (which blocks the path from income to heart disease and makes health consciousness irrelevant), or both. The backdoor criterion tells you what's sufficient.

However, if you don't know about the income variable, or if you think health consciousness fully mediates the effect of income on heart disease, you'll draw the wrong graph and reach the wrong conclusion about what to control. You might think controlling for health consciousness is enough when it isn't. You haven't eliminated the alternative explanation; you've failed to recognize it exists.

The assumptions encoded in a DAG are just formal statements about alternative explanations and how they operate. Each arrow (or absence of an arrow) represents a claim about the data generating process. Backdoor paths are literally the alternative explanations. The backdoor criterion is a systematic procedure for identifying which variables you need to condition on to block those alternatives. D-separation is a mathematical statement that you've successfully eliminated the spurious associations. The causal graph formalizes your understanding of confounding, but drawing the correct graph requires you to actually know what the confounders are and how they relate to each other.

### The Real Work of Causal Inference

Both frameworks can be seen as formalizing the process of ruling out competing explanations for an observed association. Potential outcomes does this through assumptions about conditional independence. The DAG approach does it through graphical heuristics for blocking non-causal paths. But neither framework can identify those competing alternatives in the first place.

The real work of causal inference isn’t technical, it's substantive. It requires talking to people who understand the topic. It requires thinking carefully about mechanisms and processes, not just running regressions or drawing graphs. The epidemiologist studying HRT needs to understand women's healthcare decisions, medical practice patterns, socioeconomic determinants of health, and cardiovascular disease mechanisms. The economist studying labor market interventions needs to understand how companies make hiring decisions, how people search for jobs, and what micro-economic factors constrain choices. The data scientist optimizing a digital product needs to understand product mechanics, the business model, user behavior and selection into usage.

Technical frameworks are valuable precisely because they make reasoning explicit and systematic. Researchers are forced to articulate their assumptions about the data generating process. They provide formal rules for translating those assumptions into valid causal estimates. They provide a check on whether your logic is internally consistent. But they really only work if you understand the domain you're studying. No amount of technical sophistication can substitute for that knowledge.

Causal inference ultimately comes down to knowing the subject matter well enough to identify the ways you could be wrong, then using experiments or statistical methods to rule them out. DAGs and potential outcomes help ensure rigor in the latter. But identifying how you could be wrong requires expertise that no equation or code can provide. Causal inference is easy once you understand this. Actually doing it well? That’s the hard part.

----
##### References

Grady D, Rubin SM, Petitti DB, Fox CS, Black D, Ettinger B, Ernster VL, Cummings SR. Hormone therapy to prevent disease and prolong life in postmenopausal women. *Ann Intern Med*. 1992; 117(12): 1016-1037.

Manson JE, Chlebowski RT, Stefanick ML, et al. Menopausal hormone therapy and health outcomes during the intervention and extended poststopping phases of the Women's Health Initiative randomized trials. *JAMA*. 2013; 310(13): 1353-1368.

Manson JE, Chlebowski RT, Stefanick ML, et al. Hormone therapy use and risk of chronic disease in the Nurses' Health Study: a comparative analysis with the Women's Health Initiative. *Am J Epidemiol*. 2017; 186(6): 696-707.

Rossouw JE, Prentice RL, Manson JE, et al. Postmenopausal hormone therapy and risk of cardiovascular disease by age and years since menopause. *JAMA*. 2007; 297(13): 1465-1477.

Stampfer MJ, Colditz GA, Willett WC, et al. Postmenopausal estrogen therapy and cardiovascular disease: ten-year follow-up from the Nurses' Health Study. *N Engl J Med*. 1991; 325(11): 756-762.

Writing Group for the Women's Health Initiative. Risks and benefits of estrogen plus progestin in healthy postmenopausal women: principal results from the Women's Health Initiative randomized controlled trial. *JAMA* 2002; 288: 321–33.

[^1]: For more spurioius correlations likely to disapear before your eyes, see [Tyler Vigen's wonderful site](https://www.tylervigen.com/spurious-correlations).

[^2]: Our understanding of HRT has evolved since 2002. Subsequent analyses found that age and time since menopause matter. Women aged 50-59 at hormone therapy initiation showed similar results in observational studies and the WHI, with some analyses suggesting potential cardiovascular benefits in younger women close to menopause (Rossouw et al. 2007; Manson et al. 2017). A 2013 re-analysis and follow-up data showed that younger women (50-59 years) or those within 10 years of menopause who took HRT had a more favorable risk-benefit ratio, including potential cardiovascular benefits (Manson et al. 2013).
