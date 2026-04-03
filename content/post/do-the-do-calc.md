---
title:       "Do-calculus for Humans"
subtitle:    "Demystifying the do-operator"
description: "Is this just a fancy way of saying control for all confounders?"
date:        2026-03-30
author:      "MJ"
image:       ""
tags:        ["causal inference", "statistics"]
categories:  ["explainer"]
draft:       false
---


The do-operator sits at the heart of Pearl's causal inference framework. At first glance, the $\text{do}()$ notation seems like nothing more than jargon that disguises something fairly easy to understand. You draw a DAG (a directed acyclic graph), find the backdoor paths, and adjust for those variables. Isn't this just a fancy way of saying "control for confounders"?

For simple problems, the do-operator is just shorthand for eliminating all confounding. But it can be useful when confounders can't be measured, because do-calculus can tell you if a causal effect is still identifiable in the data. Whether that matters in practice depends on how much you trust your DAG. This post works through a concrete example to show what the do-operator does, where it goes beyond the basics, and when it can be useful.

### Seeing Is Not Doing

Suppose a university wants to know whether taking a prep course improves scores on the SAT. They've assembled a dataset on about 10,000 students to try to answer this question. Here is what the simulated data looks like.

| | No Prep | Prep | Overall |
|:---|---:|---:|---:|
| Students | 6,929 | 3,558 | 10,487 |
| Female (%) | 51% | 54% | 52% |
| SAT Score | 1,021 | 1,159 | 1,068 |
| Family Income (k) | 71k | 85k | 76k |
| Hours Studied | 9.5 | 22.0 | 13.7 |
| GPA | 3.45 | 3.59 | 3.50 |

Students who took a prep course scored 138 points higher on average. But students who take a prep course are different from those who don't. They come from wealthier families, are more academically motivated, and have stronger academic records. The 138-point gap reflects the prep course plus all the other ways prep-takers were going to outscore non-takers anyway.

A DAG makes the confounding visible.

{{< figure src="/img/posts/do-calculus/sat-dag.svg" caption="A directed acyclic graph for the SAT prep example. Each arrow represents a direct causal relationship. Red arrows trace confounding paths. The dashed blue arrow is the causal effect we want to estimate." class="img-center" width="90%" >}}

The arrows encode how background factors feed into both the decision to take prep and SAT performance directly.

In notation, the naive comparison is expressed:

$E[\text{SAT} \mid \text{Prep} = 1] - E[\text{SAT} \mid \text{Prep} = 0]$.

This conditions on who *chose* prep, and by doing so, it also conditions on all the factors that influenced that choice. These are the backdoor paths, and they inflate the estimate.

The causal question requires a different condition:

$E[\text{SAT} \mid \text{do}(\text{Prep} = 1)] - E[\text{SAT} \mid \text{do}(\text{Prep} = 0)]$.

The $\text{do}$ means we're not looking at who chose prep. We're asking what would happen if we *assigned* students to prep (or not), the way a randomized experiment would. Forcing prep to take the value of 1 or 0 neutralizes all the reasons students select into the course. This counterfactual situation doesn't exist in the data. The do-operator just lets us pretend that it does.

To apply the $\text{do}$ operator, we perform graph surgery by deleting every arrow pointing into the Prep Course node. In a randomized experiment, nothing about a student's background determines whether they take prep. The incoming arrows represent those background causes, and deleting them is the graphical way of saying these variables are irrelevant.

{{< figure src="/img/posts/do-calculus/sat-dag-do.svg" caption="The graph under do(Prep), known in the literature as the 'mutilated graph.' Arrows into Prep Course have been severed (gray dashed), breaking every backdoor path. The highlighted node is now set externally rather than determined by confounders." class="img-center" width="90%" >}}

In the updated graph, Prep Course sits alone with no parents. The confounders haven't disappeared, but their influence on prep has. Any remaining association between Prep and SAT Score flows through the causal arrow. That's exactly the quantity $P(\text{SAT} \mid \text{do}(\text{Prep}))$ represents.

### The Adjustment Formula

We can only delete the paths in theory. We didn't run an experiment. But under the right conditions, we can use the data to compute what an experiment would have shown.

The most common approach is backdoor adjustment. Instead of comparing all prep-takers to non-takers, compare them *within* groups that share the same background. Using income as an example, you compute the effect of prep within each level (low, middle, high) and average those effects together, weighted by each group's share of the sample. The confounding from income washes out.

{{% notation-box %}}

**The Backdoor Adjustment Formula**

$$P(Y \mid \text{do}(X)) = \sum_z P(Y \mid X, Z=z) \, P(Z=z)$$

Calculate the treatment effect among people with the same confounder values ($Z = z$), then average across all confounder values weighted by how common they are in the sample. $Z$ must block all backdoor paths from $X$ to $Y$ and must not include anything caused by the treatment.

The weighting by $P(Z=z)$ is what separates this from a simple subgroup analysis. Without it, the confounder profiles most common among the treated group would be over-represented, reintroducing the selection bias you're trying to eliminate. The population weights put everyone on equal footing.

{{% /notation-box %}}

Here's what the adjustment looks like when we stratify by income alone — an incomplete adjustment, to show why one confounder isn't enough.

| Income Group | Share of Population | Prep Tx Effect | Weighted |
|:---|---:|---:|---:|
| Low (< 65k) | 33.3% | +109 pts | 36 |
| Middle (65k–87k) | 33.4% | +108 pts | 36 |
| High (> 87k) | 33.3% | +113 pts | 37 |
| **Adjusted estimate** | | | **+110 pts** |

The new estimate is 110 points. We've reduced the bias, but we're still way off. Income alone doesn't capture the confounding through motivation and GPA.

{{< figure src="/img/posts/do-calculus/confounded-vs-adjusted.svg" caption="<strong>Left:</strong> The naive comparison shows a 138-point gap between prep and no-prep students. <strong>Right:</strong> After stratifying by income tercile, the within-stratum differences barely budge. Income alone doesn't capture the confounding through motivation and GPA." class="img-center" width="95%" >}}

##### Regression Works Too

The adjustment formula is just stratification by another name. You can also accomplish backdoor adjustment by adding the confounders to a regression of Y on X.

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

<mark>The adjustment formula, graph surgery, and regression are all doing the same thing.</mark> The graph surgery tells you *what* confounding to remove. The formula tells you *which* variables accomplish that removal. Regression does the removing.

The $\text{do}$-operator is the notation that connects all three. The critical observation is that $P(Y \mid \text{do}(X))$ is NOT the same as $P(Y \mid X)$. To see why, look at what $P(Y \mid X)$ actually computes. When we calculate $P(\text{SAT} \mid \text{Prep} = 1)$, the people contributing to that value are disproportionately wealthy, motivated, and high-GPA, because those are the people who chose to do prep. The average is tilted toward students who would have scored well regardless. That's why the naive estimate is 138 points.

$P(\text{SAT} \mid \text{do}(\text{Prep} = 1))$ asks a different question: what if *everyone* were assigned to prep, regardless of background? The adjustment formula accomplishes this by reweighting. Instead of letting the confounder distribution of prep-takers drive the average, it weights each confounder stratum by its share of the overall population. That's what the $P(Z=z)$ term does. If you adjust for every confounder, the estimate will drop from 138 to something close to the true effect of 55.

### When the Backdoor Fails

Up to this point, the do-operator hasn't told us anything beyond the backdoor criterion alone. Do-calculus becomes useful when the backdoor criterion fails. To fully block the backdoor paths, we need to adjust for academic motivation. But motivation isn't in our dataset. Since it affects both whether a student takes prep and how well they score, there's a backdoor path we can't block.

But remember we have data on how many hours each student studied per week. Prep courses increase study time, and study time improves scores. If the entire causal effect of prep on SAT scores flows through hours studied, which is a *very* strong assumption, we have a front-door path.

{{< figure src="/img/posts/do-calculus/frontdoor-dag.svg" caption="The front-door setup. Motivation confounds Prep Course and SAT Score (dashed arrows), but the causal effect flows entirely through Hours Studied." class="img-center" width="90%" >}}

The front-door criterion exploits the fact that Hours Studied sits between Prep and SAT. That position lets us estimate the effect of prep on hours and the effect of hours on SAT separately, then chain them together.

**Piece one: the effect of Prep on Hours Studied.** Motivation makes some students more likely to take prep, and motivation also makes them study more. But in this DAG, motivation only reaches hours studied through the Prep Course node. So the observed relationship between prep and hours is unconfounded. Students who take the course study about 11 more hours on average. No adjustment needed.

**Piece two: the effect of Hours Studied on SAT Score.** This one is trickier. Motivation affects SAT scores directly, and it reaches hours studied indirectly through Prep. That creates a backdoor path: Hours ← Prep ← Motivation → SAT. But Prep is on that path, so adjusting for it blocks the confounding. Among students who all took prep (or all didn't), the variation in hours studied is no longer driven by the choice to take prep. Controlling for Prep holds the selection process constant, so within each group the relationship between hours and SAT scores reflects studying time, not differences in who chose to enroll.

{{< do-calculus-viz >}}

Chain the two pieces together. Prep adds about 11 hours of study. Each additional hour adds about 5 SAT points (estimated from piece two). Multiply them and you get roughly 54 points. Far below the naive 138-point gap, and right near the true effect of 55. All without ever measuring motivation.[^1]

{{% notation-box %}}

**The Front-Door Formula**

$$P(Y \mid \text{do}(X)) = \sum_m P(M = m \mid X) \sum_x P(Y \mid M = m, X = x) \, P(X = x)$$

where $M$ is the mediator (Hours Studied), $X$ is the treatment (Prep Course), and $Y$ is the outcome (SAT Score). The first sum captures the effect of treatment on the mediator. The second is itself a backdoor adjustment: it estimates $P(Y \mid \text{do}(M=m))$ by adjusting for $X$, which blocks the backdoor path Hours ← Prep ← Motivation → SAT.

{{% /notation-box %}}

#### Front-Door in Practice

The front-door formula also reduces to two regression models, run in sequence.

**Step 1.** Regress Hours Studied on Prep Course. No controls needed, because the DAG tells us this relationship is unconfounded:

$$\widehat{\text{Hours}} = 10.0 + \mathbf{11.0} \cdot \text{Prep}$$

Prep adds 11 hours of study.

**Step 2.** Regress SAT Score on Hours Studied, controlling for Prep to block the backdoor path (Hours ← Prep ← Motivation → SAT):

$$\widehat{\text{SAT}} = 973 + \mathbf{4.9} \cdot \text{Hours} + 84.5 \cdot \text{Prep}$$

Each additional hour of studying adds 4.9 SAT points.

**Multiply the two coefficients** and you have the front-door causal estimate: $11.0 \times 4.9 \approx 54$ points. Close to the true effect of 55, and nowhere near the naive 138.

---

{{< figure src="/img/posts/do-calculus/frontdoor-estimation.svg" caption="The front-door estimation in three steps. <strong>Left:</strong> Prep courses increase hours studied by about 11 hours. <strong>Center:</strong> Within each prep group, more hours studied predicts higher SAT scores. <strong>Right:</strong> Chaining these effects yields a front-door causal estimate (blue) much smaller than the naive comparison (red dashed), which is inflated by confounding." class="img-center" width="100%" >}}

---

Notice the coefficient on Prep in Step 2 is 84 points. That coefficient absorbs the association between Prep and SAT that runs through the backdoor (Prep ← Motivation → SAT) rather than through Hours. By soaking up that confounding, it frees the Hours coefficient to reflect only the causal effect of studying. This is the same logic the front-door formula encodes, expressed as two fitted models instead of nested summations.

This front-door analysis relies on the strong assumption that motivation affects study hours *only* through the decision to take prep. This is unlikely to be true. Motivated students are going to study more regardless of whether they take a prep course. The point is to show the method, not to defend this particular DAG.

### Where the Rules Come In

The front-door formula was derived from three rules that together make up do-calculus. Think of a DAG as a network of pipes. Association flows through them like water. Every arrow is a pipe, every node is a junction, and an intervention is a valve that shuts off all incoming pipes to a node. Graph surgery, which we used earlier to define the do-operator, is literally closing valves.

The problem is that every $\text{do}()$ in a formula represents a valve we turned in theory but never actually touched in the real data. To get an answer from observational data, every $\text{do}()$ has to go. The three rules of do-calculus tell you when it's safe to remove one.

Each rule answers a simple question about the plumbing:

| | Heuristic | What it checks |
|:---|:---|:---|
| **Rule 1** | **Irrelevant gauge** | This variable isn't connected to the outcome in the current pipe network. Reading the gauge tells you nothing new. Ignore it. |
| **Rule 2** | **Seeing = doing** | There's no backdoor plumbing between treatment and outcome. Water only flows forward, so reading the gauge gives the same answer as turning the valve yourself. Swap the intervention for an observation. |
| **Rule 3** | **Dead valve** | This valve controls a pipe that no longer connects to the outcome. It's redundant. Remove it. |

That's the entire do-calculus. Three ways to simplify, applied repeatedly until every $\text{do}()$ is gone. Each application follows the same procedure:

> 1. Pick a $\text{do}()$ you want to eliminate
> 2. Trim the pipe network (each rule specifies which pipes to cut)
> 3. Check: is water still flowing between the two nodes?
> 4. If not, simplify

Here's how that procedure derives the front-door result. We start with what we want, the causal effect of Prep on SAT, but we can't compute it directly because of unmeasured motivation. Do-calculus gives us a way to rewrite it in terms of things we *can* compute.

Since the effect of Prep on SAT flows entirely through Hours Studied, we can split the problem into two pieces: the effect of Prep on Hours, and the effect of Hours on SAT.[^2] Both still have $\text{do}()$ operators that need to go.

**Move 1: Does prep affect hours studied? (Seeing = doing)**

We want the effect of assigning prep on hours studied. Close the incoming pipes to Prep (that's what $\text{do}$ means). Now check the plumbing: is there any backdoor path between Prep and Hours? Motivation flows into Prep, but we just shut those pipes off. The only remaining connection runs forward, from Prep to Hours. Water flows one way. Reading the gauge (observing who took prep) gives the same answer as turning the valve (assigning prep). So we can replace the intervention with plain observation and estimate this piece directly from the data.

**Move 2: Does hours studied affect SAT scores? (Seeing = doing, then dead valve)**

This one is trickier, because there *is* a backdoor path: Hours ← Prep ← Motivation → SAT. We can't just observe hours studied and call it causal. We need to intervene on hours, but we don't have that experiment either. So we apply the rules in sequence.

First, **seeing = doing in reverse.** If we close the incoming pipes to Prep and also close the outgoing pipes from Hours, then SAT and Hours are disconnected. That means we can swap our observation of Hours for an intervention on Hours without changing the answer.

Now we have interventions on both Prep and Hours. But with Hours intervened on, does the valve on Prep still matter? Prep has no direct pipe to SAT. The only path from Prep to SAT ran through Hours, and we've already taken control of Hours. **Dead valve.** Drop the intervention on Prep.

We're left with the effect of intervening on Hours. The backdoor from Hours to SAT runs through Prep (Hours ← Prep ← Motivation → SAT), but adjusting for Prep blocks it. **Seeing = doing** one more time, with Prep as the adjustment variable.

Every valve is gone. The entire expression is now estimable from observational data.

{{% notation-box %}}

**The derivation in notation.** The intuitive walkthrough above corresponds to these algebraic steps. First, split through the mediator (law of total probability):

$$P(\text{SAT} \mid \text{do}(\text{Prep})) = \sum_h P(\text{SAT} \mid \text{do}(\text{Prep}), H\!=\!h) \; P(H\!=\!h \mid \text{do}(\text{Prep}))$$

Move 1 (Rule 2): $P(H \mid \text{do}(\text{Prep})) = P(H \mid \text{Prep})$

Move 2 (Rules 2, 3, then 2 again):

$P(\text{SAT} \mid \text{do}(\text{Prep}), H\!=\!h) = P(\text{SAT} \mid \text{do}(\text{Prep}), \text{do}(H\!=\!h)) = P(\text{SAT} \mid \text{do}(H\!=\!h))$

$= \sum_x P(\text{SAT} \mid H\!=\!h, \text{Prep}\!=\!x)\, P(\text{Prep}\!=\!x)$

{{% /notation-box %}}

Three rules, applied as "check the pipes," derived a formula we couldn't have gotten from the backdoor criterion alone.

### When Does It Matter

The do-operator is the mathematical notation that makes graph surgery precise. It translates "delete the paths" into a probability statement, $P(Y \mid \text{do}(X))$, that you can manipulate with algebra. Do-calculus is the set of rules for that manipulation. If a causal effect can be identified from your DAG and your data, the rules will find the formula.

If you can measure all the confounders, you really don't need to think about do-calculus. The backdoor criterion handles it. Draw a DAG, identify the adjustment set, run your regression. Most applied causal inference happens here, and the do-operator is just a notation for what you're already doing.

However, if you can't measure a key confounder, do-calculus can tell you whether you're stuck. The front-door criterion is one example, but there are others. Instrumental variable setups, mediation-based strategies, and more exotic identification paths all fall out of the same three rules. Without do-calculus, you'd have to discover each strategy separately. With it, you have a systematic procedure.

The most valuable thing do-calculus provides is the negative case. Knowing that a causal effect *cannot* be identified from your data, given your assumptions, is arguably more useful than any formula it derives. It stops you from running analyses that look rigorous but aren't. It tells you when you need better data, a different design, or stronger assumptions.

----
##### References

Pearl, J. (1995). Causal diagrams for empirical research. *Biometrika*, *82*(4), 669-688.

Pearl, J. (2012). The do-calculus revisited. *Proceedings of the 28th Conference on Uncertainty in Artificial Intelligence (UAI)*, 3-11.

Glymour, M., Pearl, J., & Jewell, N. P. (2016). *Causal Inference in Statistics: A Primer*. Wiley.

Huang, Y., & Valtorta, M. (2006). Pearl's calculus of intervention is complete. *Proceedings of the 22nd Conference on Uncertainty in Artificial Intelligence (UAI)*, 217-224.

Shpitser, I., & Pearl, J. (2006). Identification of joint interventional distributions in recursive semi-Markovian causal models. *Proceedings of the 21st National Conference on Artificial Intelligence (AAAI)*, 1219-1226.


[^1]: Anyone familiar with mediation analysis will recognize the front-door adjustment as nothing more than the indirect effect, $\alpha\beta$, where $\alpha$ is the coefficient on the path from $X$ to the mediator, and $\beta$ is the coefficient on the path from the mediator to $Y$. The indirect effect equals the total effect only when the effect of $X$ on $Y$ is fully mediated. This is a very strong assumption that is almost never true.

[^2]: The law of total probability says you can break any probability into a weighted sum over the values of another variable: $P(A) = \sum_b P(A \mid B = b) \, P(B = b)$. Here we're doing the same thing, but inside a world where Prep has been set by intervention. We split the effect of Prep on SAT into a sum over all possible values of Hours Studied, weighting each by how likely it is under the intervention.