---
title:       "Do-calculus for Humans"
subtitle:    "Demystifying the do-operator"
description: "Is it just a fancy way of saying control for all confounders?"
date:        2026-04-05
author:      "MJ"
image:       ""
tags:        ["causal inference", "statistics"]
categories:  ["explainer"]
draft:       false
---


Pearl's structural approach to causal inference is built around the construction and anlaysis of DAGs (i.e., directe acyclic graphs). We covered the basic idea in the post [Causal Inference is Easy.](/post/causal-inference-is-easy/) In many cases, applying this framework boils down to measuring and adjusting for confounding variables. A key insight is that when working with purely observational data, controlling for all confounders is equivalent to assigning the treatment level, as we would in an experiment. This claim rests on a curious concept: the do-operator.

At first glance, $\text{do()}$ looks like esoteric notation used to express the simple directive to control for confounds. However, that interpretation only holds when key confounders are measurable. When we can't measure all confounds, the utility of the do-operator becomes clear. In such cases, the rules of do-calculus provide a system for determining whether a causal effect is identifiable from data given a set of assumptions about the data generating process. If identificaiton is possible, do-calculus produces a formula for estimating the treatment effect. It can also tell you when the data are not capable of recovering the target estimand.

The goal of this post is to demistify the do-operator using a concrete example to show what it does and when it can be useful. We start with the straightforward case when all confounders are measured. The backdoor adjustment handles everything and the do-operator is just shorthand for that process. Then we'll look at the common and complicated situation where a key confound goes unmeasured. We'll show how do-calculus produces the front-door formula from three rules.

### Seeing vs. Doing

Suppose a university wants to know whether taking a prep course improves scores on the SAT. They've assembled a dataset on about 10,000 students to try to answer this question. Here is what the simulated data looks like.

| | No Prep | Prep | Overall |
|:---|---:|---:|---:|
| Students | 6,929 | 3,558 | 10,487 |
| Female (%) | 51% | 54% | 52% |
| SAT Score | 1,021 | 1,159 | 1,068 |
| Family Income (k) | 71k | 85k | 76k |
| GPA | 3.45 | 3.59 | 3.50 |

Students who took a prep course scored 138 points higher on average. But students who take a prep course are different from those who don't. They tend to come from households with higher incomes, are more academically motivated, and have stronger academic performance. The 138-point gap reflects the prep course plus all the other ways prep course takers were going to outscore non-takers anyway.

A DAG makes these confounding pathways visible.

{{< figure src="/img/posts/do-calculus/sat-dag.svg" caption="A directed acyclic graph for the SAT prep example. Each arrow represents a direct causal relationship. Red arrows trace confounding paths. The dashed blue arrow is the causal effect we want to estimate." class="img-center" width="90%" >}}

The arrows encode how background factors drive both the decision to take a prep course and SAT performance itself.

In notation, the naive comparison can be expressed:

$E[\text{SAT} \mid \text{Prep} = 1] - E[\text{SAT} \mid \text{Prep} = 0]$.

The comparison conditions on choosing to take a prep course. Because that choice was driven by motivation, income, and academic performance, those factors vary systematically between the two groups. The backdoor paths remain open, and the estimate is biased.

Answering the causal question requires a different condition:

$E[\text{SAT} \mid \text{do}(\text{Prep} = 1)] - E[\text{SAT} \mid \text{do}(\text{Prep} = 0)]$.

The $\text{do()}$ means we need to estimate what would happen if we *assigned* students to prep (or not), the way a randomized experiment would. Forcing prep to take the value of 1 or 0 neutralizes all the reasons students select into the course. The do-operator is how we figure out whether that counterfactual is hiding in the data.

To apply the $\text{do}$ operator, we perform graph surgery by deleting every arrow pointing into the Prep Course node. In a randomized experiment, nothing about a student's background determines whether they take prep. The incoming arrows represent those background causes, and deleting them is the graphical way of saying these variables are irrelevant.

{{< figure src="/img/posts/do-calculus/sat-dag-do.svg" caption="The graph under do(Prep), sometimes referred to as a 'mutilated graph.' Arrows into Prep Course have been severed (gray dashed), closing every backdoor path. The highlighted node is now set externally rather than determined by confounders." class="img-center" width="90%" >}}

In the updated graph, Prep Course sits alone with no parents. The confounders haven't disappeared, but their influence on prep has. Any remaining association between Prep and SAT Score flows through the causal arrow. That's exactly the quantity P(SAT | do(Prep)) represents.

### The Adjustment Formula

We didn't run an experiment so we can only delete the paths in theory. But under the right conditions, we can use the data to estimate what an experiment would have shown.

The most common approach is backdoor adjustment. Instead of comparing all prep-takers to non-takers, compare them *within* groups that share the same background. Using income as an example, compute the effect of prep within each level (low, middle, high) and average those effects together, weighted by each group's share of the sample. The confounding from income washes out.

{{% notation-box %}}

**The Backdoor Adjustment Formula**

$$P(Y \mid \text{do}(X)) = \sum_z P(Y \mid X, Z=z) \, P(Z=z)$$

This formula says: Calculate the treatment effect among people with the same confounder values ($Z = z$), then average across all confounder values weighted by how common they are in the sample. $Z$ must block all backdoor paths from $X$ to $Y$ and must not contain any descendant of $X$.

Weighting the average by $P(Z=z)$ is what separates this from a simple subgroup analysis. Without it, the confounder values most common among the treated group would be over-represented, reintroducing the selection bias we are trying to eliminate. The population weights put everyone on equal footing.

{{% /notation-box %}}

Here's what the adjustment looks like when we stratify by income alone.

| Income Group | Share of Population | Prep Tx Effect | Weighted |
|:---|---:|---:|---:|
| Low (< 65k) | 33.3% | +109 pts | 36 |
| Middle (65k–87k) | 33.4% | +108 pts | 36 |
| High (> 87k) | 33.3% | +113 pts | 37 |
| **Adjusted estimate** | | | **+110 pts** |

The new estimate is 110 points. We've reduced the bias, but we're still way off. Income alone doesn't capture the confounding through motivation and GPA.

{{< figure src="/img/posts/do-calculus/confounded-vs-adjusted.svg" caption="<strong>Left:</strong> The naive comparison shows a 138-point gap between prep and no-prep students. <strong>Right:</strong> After stratifying by income group, the within-stratum differences barely budge. Income alone doesn't capture the confounding through motivation and GPA." class="img-center" width="95%" >}}

Epidemiologists will recognize the adjustment formula as stratification by another name. You can also accomplish backdoor adjustment by adding the confounders to a regression of Y on X.[^2]

With no controls, a regression of SAT on Prep gives us exactly the naive comparison:

$$\widehat{\text{SAT}} = 1021 + \mathbf{138} \cdot \text{Prep}$$

Add income as a control and the coefficient on Prep drops:

$$\widehat{\text{SAT}} = 843 + \mathbf{102} \cdot \text{Prep} + 2.5 \cdot \text{Income}$$

Add GPA and it drops to 74. And if we could somehow measure motivation and include it too:

$$\widehat{\text{SAT}} = 326 + \mathbf{56} \cdot \text{Prep} + 0.6 \cdot \text{Income} + 194 \cdot \text{GPA} + 92 \cdot \text{Motivation}$$

---
| Model | Controls | Prep Coefficient |
|:---|:---|---:|
| Naive | None | +138 pts |
| + Income | Income | +102 pts |
| + Income, GPA | Income, GPA | +74 pts |
| + Motivation | Income, GPA, Motivation | +56 pts |

As we add controls, the coefficient for SAT prep approaches the true effect of 55 points. The last model is hypothetical, since motivation is unmeasured. That gap between 74 and 56 is the bias from the unmeasured confounder.

<mark>The adjustment formula, graph surgery, and regression are all doing the same thing.</mark> The graph surgery tells you *what* confounding to remove. The formula tells you how to accomplish that removal. Regression does the removing.

### When the Backdoor Fails

This works cleanly when the confounders are measurable. In the SAT example, income and GPA are in the dataset. Motivation isn't and that gap is exactly where backdoor adjustment comes up short. Because motivation affects both whether a student takes a prep course and how well they score, there's a backdoor path we can't block. This is where do-calculus becomes useful.

But we do have data on how many hours each student studied per week. Prep courses increase study time, and study time improves scores. For the sake of simplicity, if we assume the entire causal effect of prep on SAT scores flows through hours studied – a *very* strong assumption – we have a front-door path.

{{< figure src="/img/posts/do-calculus/frontdoor-dag.svg" caption="The front-door setup. Motivation confounds Prep Course and SAT Score (dashed arrows), but the causal effect flows entirely through Hours Studied." class="img-center" width="90%" >}}

The front-door criterion exploits the fact that Hours Studied sits between Prep and SAT. That position lets us split the problem into two pieces and chain them together.

**Piece one: Prep → Hours Studied.** Motivation makes some students more likely to take prep, and motivation also makes them study more. But in this DAG, motivation only reaches hours through a prep course, which means there's no backdoor between prep and hours. This is one of three conditions the front-door criterion requires. Students who take the course study about 11 more hours on average. No adjustment needed.

**Piece two: Hours Studied → SAT Score.** This one is trickier. Motivation affects SAT scores directly, and it reaches hours studied through prep course completion. That opens a backdoor: Hours ← Prep ← Motivation → SAT. To close it, we control for prep. Among students who took prep, variation in hours studied is no longer driven by motivation. Within each group, hours and scores tell a clean story.

#### Front-Door in Practice

Here's what those two pieces look like as regressions.

**Step 1.** Regress Hours Studied on Prep Course. No controls needed:

$$\widehat{\text{Hours}} = 10.0 + \mathbf{11.0} \cdot \text{Prep}$$

Prep adds 11 hours of study.

**Step 2.** Regress SAT Score on Hours Studied, controlling for Prep to block the backdoor:

$$\widehat{\text{SAT}} = 973 + \mathbf{4.9} \cdot \text{Hours} + 84.5 \cdot \text{Prep}$$

Each additional hour of studying adds 4.9 SAT points.

**Multiply the two coefficients** and you have the front-door causal estimate: $11.0 \times 4.9 \approx 54$ points. Close to the true effect of 55, nowhere near the naive 138, and all without ever measuring motivation.[^1]

---

{{< figure src="/img/posts/do-calculus/frontdoor-estimation.svg" caption="The front-door estimation in three steps. <strong>Left:</strong> Prep courses increase hours studied by about 11 hours. <strong>Center:</strong> Within each prep group, more hours studied predicts higher SAT scores. <strong>Right:</strong> Chaining these effects yields a front-door causal estimate (blue) much smaller than the naive comparison (red dashed), which is inflated by confounding." class="img-center" width="100%" >}}

---

That's the front-door formula in practice. In formal notation:

{{% notation-box %}}

**The Front-Door Formula**

$$P(Y \mid \text{do}(X)) = \sum_m \Bigl[ \underbrace{P(M = m \mid X)}_{\text{Piece 1}} \cdot \underbrace{\sum_x P(Y \mid M = m, X = x) \, P(X = x)}_{\text{Piece 2}} \Bigr]$$

where $M$ is the mediator (Hours Studied), $X$ is the treatment (Prep Course), and $Y$ is the outcome (SAT Score). For each possible value of hours studied $m$, you multiply Piece 1 (how likely that hours level is under prep) by Piece 2 (the expected SAT outcome at that hours level, averaged over the prep distribution), then sum over all values of $m$. The inner sum over $x$ in Piece 2 is what controlling for Prep in the regression does: it averages the Hours → SAT relationship over the full population distribution of Prep rather than within any particular hours level. In the linear case, this reduces to multiplying two regression coefficients.

{{% /notation-box %}}

Notice the Prep coefficient in Step 2 is 84 points. That coefficient absorbs the association between Prep and SAT that runs through the backdoor (Prep ← Motivation → SAT) rather than through Hours. By soaking up that confounding, it frees the Hours coefficient to reflect only the causal effect of studying. This is the same logic the front-door formula encodes, expressed as two fitted models instead of nested summations.

This front-door estimate relies on the strong assumption that motivation affects study hours *only* through the decision to take prep. Motivated students are going to study more regardless of whether they take a prep course, which makes that assumption unlikely to hold. The point is to illustrate the method, not to defend this particular DAG. That said, the front-door adjustment is rarely used in practice because the required conditions are difficult to find in real-world data.

### Time To Follow The Rules

Up to this point, we've taken the front-door formula as a given. Seeing how it was derived can be helpful for understanding what makes do-calculus useful. We need to first cover the three rules of do-calculus. Each rule describes a condition under which you can replace a hypothetical experiment with a plain observation. That's do-calculus in a nutshell: figure out how to turn "what if I had assigned treatment?" into "here's what I measured."

**Rule 1** lets you remove a variable from a probability expression when graph surgery has made it irrelevant to the outcome. Suppose you're computing P(SAT | do(Prep), Z) for some variable Z. If Z has no active path to SAT in the mutilated graph, conditioning on it changes nothing, and you can simplify to P(SAT | do(Prep)). In the SAT example, household income and GPA influence scores only by affecting who takes prep. After do(Prep) severs all incoming arrows to the Prep node, those variable are cut off from the outcome and can be dropped.

**Rule 2** lets you swap a do() intervention for an observation when the two are equivalent in the *modified* graph. The condition is that all backdoor paths into the intervened on node are closed, leaving only forward-flowing causal paths. When that holds, observing the variable gives the same answer as assigning it externally. In the SAT example, after do(Prep) severs all incoming arrows to Prep, there's no backdoor from Prep to Hours and motivation's path into Prep is cut. So P(H | do(Prep)) and P(H | Prep) are the same quantity. You don't need to imagine a randomized experiment; just look at who took the course. Rule 2 also runs in the other direction. If you have an observed variable but realize a backdoor is still open, you can insert a do() to represent the intervention needed to close it. That's how Hours enters Piece two below.

**Rule 3** lets you drop do() intervention entirely when the intervened-on variable has no remaining path to the outcome given the other terms in the probability expression. Just as Rule 1 removes an irrelevant observation, Rule 3 removes an irrelevant do(). In the SAT derivation, once both Prep and Hours are intervened on, we have P(SAT | do(Prep), do(H=h)). Prep's only route to SAT ran through Hours, but Hours is now set. With that path blocked, do(Prep) can't reach SAT through any channel. Rule 3 says drop it, leaving P(SAT | do(H=h)).

Our goal is to estimate, P(SAT | do(Prep)), the causal effect of taking a prep course on SAT. To do that, we need to eliminate do(Prep) and replace it with observations available in the data. The only route from Prep to SAT runs through Hours. We need to first expand the expression through the mediator (hours) and bring it into the expression. That requires applying the law of total probability.[^3]

$$P(\text{SAT} \mid \text{do}(\text{Prep})) = \sum_h P(\text{SAT} \mid \text{do}(\text{Prep}), H\!=\!h) \; P(H\!=\!h \mid \text{do}(\text{Prep}))$$

Now we have two do(Prep), one for each of the two pieces we need to estimate.

**Piece one: does prep affect hours?** Apply the do-operator to close the incoming paths. Now the only path from Prep to Hours runs forward through the causal arrow. Motivation used to flow into Prep, but that pipe is cut. No backdoor survives. Seeing who took prep tells us the same thing as assigning prep ourselves. **Rule 2**: swap the Prep intervention for an observation.

$$P(H \mid \text{do}(\text{Prep})) = P(H \mid \text{Prep})$$

**Piece two: does hours affect SAT?** We start with P(SAT | do(Prep), H=h): Prep is intervened on, Hours is observed. There's a backdoor from Hours to SAT running back through Prep and Motivation. We can't simply observe hours and call it causal. We need to close the incoming pipes to Hours. **Rule 2**: insert do(H), converting the observation into an intervention:

$$P(\text{SAT} \mid \text{do}(\text{Prep}), H\!=\!h) = P(\text{SAT} \mid \text{do}(\text{Prep}), \text{do}(H\!=\!h))$$

With those paths closed, the influence of Hours only flows forward into SAT, so observing H gives the same result as intervening on H. Now both Prep and Hours are intervened on. Do we still need the do(prep)? With Hours fixed, Prep has no remaining path to SAT. **Rule 3**: drop do(Prep). We're left with

$$P(\text{SAT} \mid \text{do}(H\!=\!h))$$

One backdoor still runs from Hours back through Prep to Motivation to SAT, but Prep is observed, so we can adjust for it. **Rule 2** one final time: replace do(H=h) with an observation, controlling for Prep.

$$\sum_x P(\text{SAT} \mid H\!=\!h, \text{Prep}\!=\!x)\, P(\text{Prep}\!=\!x)$$

Every intervention is gone and we have the two required pieces, which are estimable from our data.

### When Does It Matter

Most applied causal inference doesn't require thinking about do-calculus. If you can measure the confounders, the backdoor criterion handles it. Draw a DAG, identify the adjustment set, and run the regression. The do-operator is just shorthand for those steps.

When a confounder is unmeasured, the rules of do-calculus show their value. The front-door criterion is one example, but the same framework covers mediation-based strategies and more exotic identification paths. Without do-calculus, each strategy requires its own insight. With it, one procedure covers all of them.

The most valuable result isn't the formula derived from the rules. It's the negative case: knowing that a causal effect *cannot* be identified from available data, given our assumptions. That stops us from running analyses that look rigorous but aren't. Knowing you're stuck is an important result. It tells you precisely what questions the data can't answer. That's more useful than a plausible-looking estimate built on unverifiable assumptions.

For most applied work, the do-operator really is just careful bookkeeping. But the three rules are what turn that bookkeeping into a guarantee. If identification is possible from the data, the rules will find a formula. If it isn't, they'll tell you that too.

----
##### References

Pearl, J. (1995). Causal diagrams for empirical research. *Biometrika*, *82*(4), 669-688.

Pearl, J. (2012). The do-calculus revisited. *Proceedings of the 28th Conference on Uncertainty in Artificial Intelligence (UAI)*, 3-11.

Glymour, M., Pearl, J., & Jewell, N. P. (2016). *Causal Inference in Statistics: A Primer*. Wiley.

Huang, Y., & Valtorta, M. (2006). Pearl's calculus of intervention is complete. *Proceedings of the 22nd Conference on Uncertainty in Artificial Intelligence (UAI)*, 217-224.

Shpitser, I., & Pearl, J. (2006). Identification of joint interventional distributions in recursive semi-Markovian causal models. *Proceedings of the 21st National Conference on Artificial Intelligence (AAAI)*, 1219-1226.


[^1]: Anyone familiar with mediation analysis will recognize the front-door adjustment as nothing more than the indirect effect, $\alpha\beta$, where $\alpha$ is the coefficient on the path from $X$ to the mediator, and $\beta$ is the coefficient on the path from the mediator to $Y$. The indirect effect equals the total effect only when the effect of $X$ on $Y$ is fully mediated. This is a very strong assumption that is almost never true.

[^2]: This equivalence holds when the treatment effect is roughly constant across confounder strata. With substantial effect heterogeneity, OLS with additive controls and the stratification formula use different implicit weights and can give different answers.

[^3]: The law of total probability says you can break any probability into a weighted sum over the values of another variable: $P(A) = \sum_b P(A \mid B = b) \, P(B = b)$. Here we're doing the same thing, but inside a world where Prep has been set by intervention. We split the effect of Prep on SAT into a sum over all possible values of Hours Studied, weighting each by how likely it is under the intervention.
