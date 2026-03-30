---
title:       "Do the Do Calculus"
subtitle:    "Demystifying the do-operator"
description: "Is this just a fancy way of saying control for all confounders?"
date:        2026-03-22
author:      "MJ"
image:       ""
tags:        ["causal inference", "statistics"]
categories:  []
draft:       false
---

The do-operator sits at the heart of Pearl's framework. At first glance, the $\text{do}()$ notation seems like nothing more than jargon for something that's easy to understand. You draw a DAG, find the backdoor paths and adjust for those variables. Isn't this just a fancy way of saying "control for confounders"?

Sort of. For the problems most of us encounter, the do-operator is equivalent to controlling for confounders. But "control for confounders" papers over real complexity. A concrete example shows where the cracks appear.

### Seeing Is Not Doing

Suppose a university wants to know whether taking a prep course improves scores on the SAT. They've assembled a dataset on about 10,000 students to try to answer this question. Here is what the (fake) sample looks like.

| | No Prep | Prep | Overall |
|:---|---:|---:|---:|
| Students | 6,929 | 3,558 | 10,487 |
| Female (%) | 51% | 54% | 52% |
| SAT Score | 1,021 | 1,159 | 1,068 |
| Family Income (k) | 71k | 85k | 76k |
| Hours Studied | 9.5 | 22.0 | 13.7 |
| GPA | 3.45 | 3.59 | 3.50 |

Students who took a prep course scored 138 points higher on average. This estimate tells us only that students who *chose to take* a prep course scored higher than those who didn't. Students who take a prep course are different from those who don't in ways that also affect their SAT scores. They tend to come from wealthier families that can pay for the course. They tend to be more academically motivated, attend higher-quality schools, and have stronger academic records. All of these factors boost SAT scores independently of any prep course. The 138-point gap reflects the effect of the prep course plus all the other ways that prep-takers were going to outscore non-takers anyway.

A DAG makes the contamination visible.

{{< figure src="/img/posts/do-calculus/sat-dag.svg" caption="A directed acyclic graph for the SAT prep example. Each arrow represents a direct causal relationship. Red arrows trace confounding paths. The dashed blue arrow is the causal effect we want to estimate." class="img-center" width="90%" >}}

The arrows encode how background factors feed into both the decision to take prep and SAT performance directly.

In notation, the naive comparison is expressed:

$E[\text{SAT} \mid \text{Prep} = 1] - E[\text{SAT} \mid \text{Prep} = 0]$.

This conditions on who *chose* prep, and by doing so, it also conditions on all the factors that influenced that choice. These are the backdoor paths, and they inflate the estimate.

The causal question requires a different condition:

$E[\text{SAT} \mid \text{do}(\text{Prep} = 1)] - E[\text{SAT} \mid \text{do}(\text{Prep} = 0)]$.

The $\text{do}$ means we're not looking at who chose prep. We're asking what would happen if we *assigned* students to prep (or not), the way a randomized experiment would. Forcing prep to take the value of 1 or 0 neutralizes all the reasons students select into the course. This counterfactual situation doesn't exist in the data. The do-operator just lets us pretend that it does.

To apply the $\text{do}$ operator we perform graph surgery by deleting every arrow pointing into the Prep Course node. In a randomized experiment, nothing about a student's background determines whether they get prep. The incoming arrows represent those background causes, and deleting them is the graphical way of saying "these causes no longer operate."

{{< figure src="/img/posts/do-calculus/sat-dag-do.svg" caption="The graph under do(Prep), known in the literature as the 'mutilated graph.' Arrows into Prep Course have been severed (gray dashed), breaking every backdoor path. The highlighted node is now set externally rather than determined by confounders." class="img-center" width="90%" >}}

In the updated graph, Prep Course has no causes. The confounders still exist and still affect SAT scores, but they no longer determine who takes prep. Any remaining association between Prep and SAT Score flows through the causal arrow. That's exactly the quantity $P(\text{SAT} \mid \text{do}(\text{Prep}))$ represents.

### The Adjustment Formula

We can't delete the paths in the real world. We didn't run an experiment. But under the right conditions, we can use the data to compute what an experiment would have shown.

The most common approach is backdoor adjustment. Instead of comparing all prep-takers to all non-takers, compare them *within groups that share the same background*. Using income as an example, you compute effect of prep within each level (low, middle, high) and average those effects together, weighted by each group's share of the sample. The confounding from income washes out.

{{% notation-box %}}

**The Backdoor Adjustment Formula**

$$P(Y \mid \text{do}(X)) = \sum_z P(Y \mid X, Z=z) \, P(Z=z)$$

Calculate the treatment effect among people with the same confounder values ($Z = z$), then average across all confounder values weighted by how common they are in the sample. $Z$ must block all backdoor paths from $X$ to $Y$ and must not include anything caused by the treatment.

The weighting by $P(Z=z)$ is what separates this from a simple subgroup analysis. Without it, the confounder profiles most common among the treated group would be over-represented, reintroducing the selection bias you're trying to eliminate. The population weights put everyone on equal footing.

{{% /notation-box %}}

Here's what the adjustment looks like when we stratify by income tercile.

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

As we add controls, the coefficient for SAT prep approaches the true effect of 55 points. We can run the first three models. The last one is hypothetical, since motivation is unmeasured. That gap between 74 and 56 is the bias from the unmeasured confounder.

<mark>The adjustment formula, graph surgery, and regression are all doing the same thing.</mark> The graph surgery tells you *what* confounding to remove. The formula tells you *which* variables accomplish that removal. Regression does the removing. The $\text{do}$-operator is the notation that connects all three: $P(Y \mid \text{do}(X))$ is NOT the same as $P(Y \mid X)$, and the formula tells you exactly what it takes to bridge the gap.

Up to this point, the do-operator hasn't told us anything beyond the backdoor criterion alone. The do-calculus becomes useful when the backdoor criterion fails. To fully block the backdoor paths, we need to adjust for academic motivation. But motivation isn't in our dataset.

### When the Backdoor Fails

Motivation is a disposition that can't be measured well. Since motivation affects both whether a student takes prep and how well they score, there's a backdoor path we can't block. The standard adjustment formula won't work because we can't condition on a variable we haven't measured.

But suppose we *can* observe how many hours each student studied per week. Prep courses increase study time, and study time improves scores. If the entire causal effect of prep on SAT scores flows through hours studied, with no shortcut that bypasses it, we have a front-door path.

{{< figure src="/img/posts/do-calculus/frontdoor-dag.svg" caption="The front-door setup. Motivation confounds Prep Course and SAT Score (dashed arrows), but the causal effect flows entirely through Hours Studied." class="img-center" width="90%" >}}

The front-door criterion works by breaking the problem into two pieces that are easier to handle.

**Piece one: the effect of Prep on Hours Studied.** Motivation makes some students more likely to take prep, and motivation also makes them study more. But in this DAG, motivation only reaches hours studied through the Prep Course node. So the observed relationship between prep and hours is unconfounded. Students who take the course study about 11 more hours on average, and that difference reflects a genuine causal effect. No adjustment needed.

**Piece two: the effect of Hours Studied on SAT Score.** This one is trickier. Motivation affects SAT scores directly, and it reaches hours studied indirectly through Prep. That creates a backdoor path: Hours ← Prep ← Motivation → SAT. But Prep is on that path, so adjusting for it blocks the confounding. Among students who all took prep (or all didn't), the variation in hours studied is no longer driven by the choice to take prep. Within those groups, the relationship between hours and SAT scores reflects the causal effect of studying.

Chain the two pieces together. Prep adds about 11 hours of study. Each additional hour adds about 5 SAT points (estimated from piece two). Multiply them and you get roughly 54 points. Far below the naive 138-point gap, and right near the true effect of 55. All without ever measuring motivation.[^1]

{{% notation-box %}}

**The Front-Door Formula**

$$P(Y \mid \text{do}(X)) = \sum_m P(M = m \mid X) \sum_x P(Y \mid M = m, X = x) \, P(X = x)$$

where $M$ is the mediator (Hours Studied), $X$ is the treatment (Prep Course), and $Y$ is the outcome (SAT Score). The first sum captures the effect of treatment on the mediator. The second is itself a backdoor adjustment: it estimates $P(Y \mid \text{do}(M=m))$ by adjusting for $X$, which blocks the confounding path between Hours Studied and SAT Score through motivation.

{{% /notation-box %}}

#### Front-Door in Practice

The front-door formula also reduces to regressions. Two of them, run in sequence.

**Step 1.** Regress Hours Studied on Prep Course. No controls needed, because the DAG tells us this relationship is unconfounded:

$$\widehat{\text{Hours}} = 10.0 + \mathbf{11.0} \cdot \text{Prep}$$

Prep adds 11 hours of study.

**Step 2.** Regress SAT Score on Hours Studied, controlling for Prep to block the backdoor through Motivation:

$$\widehat{\text{SAT}} = 973 + \mathbf{4.9} \cdot \text{Hours} + 84.5 \cdot \text{Prep}$$

Each additional hour of studying adds 4.9 SAT points.

**Multiply the two coefficients** and you have the front-door causal estimate: $11.0 \times 4.9 \approx 54$ points. Close to the true effect of 55, and nowhere near the naive 138.

---

{{< figure src="/img/posts/do-calculus/frontdoor-estimation.svg" caption="The front-door estimation in three steps. <strong>Left:</strong> Prep courses increase hours studied by about 11 hours. <strong>Center:</strong> Within each prep group, more hours studied predicts higher SAT scores. <strong>Right:</strong> Chaining these effects yields a front-door causal estimate (blue) much smaller than the naive comparison (red dashed), which is inflated by confounding." class="img-center" width="100%" >}}

---

Notice the coefficient on Prep in Step 2: +84 points. That's all the confounding from motivation that would normally bias a naive analysis. By including Prep in the regression, we absorb that confounding so the Hours coefficient reflects only the causal effect of studying. This is the same logic the front-door formula encodes, expressed as two fitted models instead of nested summations.

This front-door analysis relies on a strong assumption: that motivation affects study hours *only* through the decision to take prep. If motivated students study more regardless of the course, the criterion breaks down. The point is to show the method, not to defend this particular DAG.

### Where the Rules Come In

The front-door formula was derived from three rules that together make up the do-calculus. Each rule answers one question: when can you remove $\text{do}()$ from a probability statement. Every $\text{do}()$ represents an intervention we didn't actually perform. We can't look up $P(Y \mid \text{do}(X))$ in a dataset the way we can look up $P(Y \mid X)$. To get an answer from observational data, every $\text{do}()$ has to go. Here's how the rules derive the front-door result.

We start with what we want: $P(\text{SAT} \mid \text{do}(\text{Prep}))$. We can't compute this directly because of unmeasured motivation. The do-calculus gives us a way to rewrite it in terms of things we *can* compute.

**Step 1. Expand through the mediator.** Since the effect of Prep on SAT flows entirely through Hours Studied, we can write

$$P(\text{SAT} \mid \text{do}(\text{Prep})) = \sum_h P(\text{SAT} \mid \text{do}(\text{Prep}), H = h) \, P(H = h \mid \text{do}(\text{Prep}))$$

where $H$ is Hours Studied. This is the law of total probability applied inside the interventional world. We still have $\text{do}$ operators to eliminate.

**Step 2. The effect of Prep on Hours (Rule 2).** Look at $P(H \mid \text{do}(\text{Prep}))$. In the surgically modified graph (arrows into Prep removed), Prep has no parents, so there can't be a common cause of Prep and Hours. No backdoor path, no confounding. Observing who took prep gives you the same answer as intervening. **Rule 2** lets us replace the $\text{do}$ with ordinary conditioning:

$$P(H \mid \text{do}(\text{Prep})) = P(H \mid \text{Prep})$$

This is piece one. We can estimate it directly from the data.

**Step 3. The effect of Hours on SAT (Rules 2 and 3).** The term $P(\text{SAT} \mid \text{do}(\text{Prep}), H = h)$ still has an intervention on Prep. We need to get rid of it, but we can't just drop $\text{do}(\text{Prep})$ and observe $H$, because motivation confounds Hours and SAT. We need $\text{do}(H)$, not just $H$.

First, **Rule 2** converts the observation of $H$ into an intervention. In the graph with arrows into Prep removed and arrows out of $H$ removed, SAT is independent of $H$ given Prep (the only path from $H$ to SAT went through the arrow we just cut). So we can replace the observation with an intervention:

$$P(\text{SAT} \mid \text{do}(\text{Prep}), H = h) = P(\text{SAT} \mid \text{do}(\text{Prep}), \text{do}(H = h))$$

Now **Rule 3** lets us drop $\text{do}(\text{Prep})$. Once we've intervened on Hours, Prep has no other path to SAT (there's no direct edge), so the intervention on Prep is redundant:

$$P(\text{SAT} \mid \text{do}(\text{Prep}), \text{do}(H = h)) = P(\text{SAT} \mid \text{do}(H = h))$$

Finally, we need to convert $\text{do}(H)$ into something observable. Motivation confounds Hours and SAT, but adjusting for Prep blocks that backdoor. **Rule 2** again converts the intervention into conditioning, with Prep as the adjustment variable:

$$P(\text{SAT} \mid \text{do}(H = h)) = \sum_x P(\text{SAT} \mid H = h, \text{Prep} = x)\, P(\text{Prep} = x)$$

Every $\text{do}$ is gone. The entire expression is now estimable from observational data.

The formal rules are stated in their general form, with multiple interventions already in play. The front-door derivation above uses the most common special case: a single intervention that needs to be converted into something estimable. The important thing isn't memorizing the notation. It's that three rules, applied mechanically, derived a formula we couldn't have gotten from the backdoor criterion alone.

### When Does It Matter

Honestly, it depends on the problem.

**If you can measure your confounders, you don't need to think about do-calculus.** The backdoor criterion handles it. Draw a DAG, identify the adjustment set, run your regression or matching estimator. Most applied causal inference lives here, and the do-operator is just a notation for what you're already doing. This is where my original skepticism was correct.

**If you can't measure a key confounder, do-calculus tells you whether you're stuck.** The front-door criterion is one example, but there are others. Instrumental variable setups, mediation-based strategies, and more exotic identification paths all fall out of the same three rules. Without do-calculus, you'd have to discover each strategy separately and hope you haven't missed one. With it, you have a systematic procedure. If the rules can eliminate all the $\text{do}$ operators, you have an identification strategy. If they can't, no amount of statistical cleverness will save you.

**You probably won't apply the rules by hand.** Algorithms like ID and IDC implement do-calculus automatically. You draw the DAG, specify what's observed, and the algorithm either returns an estimable formula or tells you identification is impossible. The `causaleffect` package in R and `DoWhy` in Python both implement these algorithms. The practical skill is drawing the right DAG, not hand-deriving formulas.

**The most valuable thing do-calculus provides is the negative result.** Knowing that a causal effect *cannot* be identified from your data, given your assumptions, is arguably more useful than any formula it derives. It stops you from running analyses that look rigorous but aren't. It tells you when you need better data, a different design, or stronger assumptions. Before do-calculus was proven complete, there was no way to know whether a failed identification attempt meant the problem was hard or impossible. Now there is.

### The Graph Carries the Knowledge

The do-operator is the mathematical notation that makes graph surgery precise. It translates "delete the arrows" into a probability statement, $P(Y \mid \text{do}(X))$, that you can manipulate with algebra. The do-calculus is the set of rules for that manipulation. And the completeness proof, established about a decade after the original rules, is the deep contribution. It guarantees that if a causal effect can be identified from your DAG and your data, the rules will find the formula. If they can't, nothing can. Earlier methods could identify some causal effects, but they couldn't tell you when identification was impossible. The do-calculus settles the question.

But the calculus is only as good as the graph you give it. Draw the wrong DAG, miss a confounder, get an arrow backwards, and the derived formula will be wrong. The rules guarantee logical consistency given your assumptions. They can't tell you whether your assumptions are right. That still requires understanding the domain. The do-calculus carries the logic. The graph carries the knowledge. Neither works without the other.


----
##### References

Pearl, J. (1995). Causal diagrams for empirical research. *Biometrika*, *82*(4), 669-688.

Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.

Pearl, J. (2012). The do-calculus revisited. *Proceedings of the 28th Conference on Uncertainty in Artificial Intelligence (UAI)*, 3-11.

Glymour, M., Pearl, J., & Jewell, N. P. (2016). *Causal Inference in Statistics: A Primer*. Wiley.

Huang, Y., & Valtorta, M. (2006). Pearl's calculus of intervention is complete. *Proceedings of the 22nd Conference on Uncertainty in Artificial Intelligence (UAI)*, 217-224.

Shpitser, I., & Pearl, J. (2006). Identification of joint interventional distributions in recursive semi-Markovian causal models. *Proceedings of the 21st National Conference on Artificial Intelligence (AAAI)*, 1219-1226.


[^1]: Anyone familiar with mediation analysis will recognize the frontdoor adjustment as nothing more than the indirect effect, $\alpha\beta$, where $\alpha$ is the coefficient on the path from $X$ to the mediator, and $\beta$ is the coefficient on the path from the mediator to $Y$. The indirect effect equals the total effect only when the effect of $X$ on $Y$ is fully mediated. This is a very strong assumption that is almost never true.