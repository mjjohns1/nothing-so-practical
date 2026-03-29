---
title:       "Do the Do Calculus"
subtitle:    ""
description: "Demystifying do-calculus, one toy example at a time"
date:        2026-03-04
author:      "MJ"
image:       ""
tags:        ["causal inference", "statistics"]
categories:  []
draft:       false
---


## Do the Do Calculus

Pearl’s causal framework is built around the structural analysis of variables and how they cause one another. At the center is the DAG: directed acyclic graph. DAGs are used to represent and encode a causal question, such as whether hormone replacement therapy reduces the risk of heart disease.

The do-operator sits at the heart of Pearl's framework. It is a mathematical tool that makes DAGs useful beyond merely visualizing cause and effect relationships. It provides a set of rules for determining when a causal question can be answered with observational data. The rules, referred to as do calculus, cover situations the backdoor criterion can't handle, and work on any DAG. To make this more concrete, let's look at an example.

### One Does Not Merely See

Suppose a university wants to know whether taking an SAT prep course improves scores on the test. The university has created a dataset of about 10,000 students to help answer this question. Here is what this sample looks like:

[DESCRIPTIVE STATS TABLE HERE]

A quick calculation shows that students who took a prep course scored 140 points higher on average. This is a sizable effect, but it’s wrong.

Think about what the 140-point gap actually tells us. Among students who *happened to take* a prep course, what were their average scores compared to students who didn't? That's just a fact about the data. But it doesn't tell us anything about the causal effect of SAT prep.

Students who chose to take prep are different from those who didn't in ways that also affect their SAT scores. They tend to come from wealthier families that can pay for the course. They tend to be more academically motivated, attend higher-quality schools, and have stronger academic records. All of these factors boost SAT scores independently of any prep course. The 140-point gap reflects the effect of the prep course plus all the other ways that students taking a course were going to outscore others.

A DAG makes the contamination visible.

{{< figure src="/img/posts/do-calculus/sat-dag.svg" caption="A directed acyclic graph for the SAT prep example. Each arrow represents a direct causal relationship. Red arrows trace confounding paths. The dashed blue arrow is the causal effect we want to estimate." class="img-center" >}}

Each arrow is a claim about what causes what. Parents' education shapes both family income and academic motivation. Family income determines access to prep courses and school quality. School quality influences GPA, motivation, and SAT scores directly. Motivation drives students to sign up for prep, to study harder, and feeds into their GPA. GPA predicts both willingness to invest in prep and performance on the SAT.


In notation, this naive difference between preppers and non-preppers can be expressed as

$E[\text{SAT} \mid \text{Prep} = 1] - E[\text{SAT} \mid \text{Prep} = 0]$.

This is another way of saying we have simply subtracted the expected SAT score (i.e., average) of students who chose to take a prep course (Prep = 1) from students who didn’t (Prep = 0). It's a comparison conditioned on what we see in the data. The important point is that by conditioning on the decision to take a prep course, we are also conditioning on all the other factors that influence that decision. These are the backdoor paths, and they're the reason the naive comparison is inflated.

To determine if taking a prep course actually *causes* higher SAT scores, requires a different condition:

$E[\text{SAT} \mid \text{do}(\text{Prep} = 1)]$.

The $\text{do}$ means we're not looking at who chose prep. We're asking what would happen if we assigned a student to prep, like you would do in a randomized experiment. Assigning a student neutralizes all the reasons students select into the course. Now, this is not a reflection of reality as we know it from the data. The do-operator allows us to consider a counterfactual situation that doesn’t exist. This becomes very useful for figuring out how to answer our causal question with the observational data we have.

To use the $\text{do}$ operator, we delete every arrow pointing *into* the Prep Course node. We're saying: forget about why students normally take prep. We're setting the value of the Prep Course variable ourselves.

{{< figure src="/img/posts/do-calculus/sat-dag-do.svg" caption="The graph under do(Prep), known in the literature as the 'mutilated graph.' Arrows into Prep Course have been severed (gray dashed), breaking every backdoor path. The highlighted node is now set externally rather than determined by confounders." class="img-center" >}}

In this graph modified by applying the do-operator, Prep Course has no parent nodes so nothing causes it. The confounders still exist and still affect SAT scores, but they no longer determine who takes prep. Any association between Prep and SAT Score that survives in this graph has to flow through the causal arrow. That's exactly the quantity $P(\text{SAT} \mid \text{do}(\text{Prep}))$ represents.

### The Adjustment Formula

Of course, we can't actually delete arrows in the real world. We didn't run an experiment. But under the right conditions, we can use the data we have to compute what the experiment *would* have shown. The most common way to do this is the backdoor adjustment formula.

Instead of comparing all prep-takers to all non-takers (which is contaminated by confounding), compare them *within groups that share the same background*. For example, among low-income students, how much higher do prep-takers score? What about amont middle-income and high-income students? If you compute the prep effect within each group and then average those effects together, weighted by how big each group is in the population, the confounding washes out. What's left is the causal effect.

{{% notation-box %}}

**The Backdoor Adjustment Formula**

$$P(Y \mid \text{do}(X)) = \sum_z P(Y \mid X, Z=z) \, P(Z=z)$$

To estimate what would happen if we *assigned* the treatment, look at the outcome among people with the same confounder values ($Z = z$), then average across all confounder values weighted by how common they are in the full population. $Z$ must block all backdoor paths from $X$ to $Y$ and must not include anything caused by the treatment.

{{% /notation-box %}}

[TABLE TO SHOW THE ADJUSTMENT FORMULA MATHEMATICALLY]

Suppose 40% of students are low-income and 20% are high-income. Among low-income students, prep-takers scored 30 points higher than non-takers. Among high-income students, the difference is 25 points. The adjusted causal effect is $0.4 \times 30 + 0.2 \times 25 = 17$ points. That's a weighted average of the within-group effects, where the weights reflect how common each group is in the *full population*, not among preppers.

The weighting by $P(Z=z)$ is what separates this from a simple subgroup analysis. Without it, you'd over-represent the confounder profiles most common among the treated group, which is the selection bias you're trying to eliminate. The population weights put everyone on equal footing.

{{< figure src="/img/posts/do-calculus/confounded-vs-adjusted.svg" caption="<strong>Left:</strong> The naive comparison shows a large gap between prep and no-prep students. <strong>Right:</strong> After stratifying by income, the within-stratum differences shrink substantially. The remaining gap is closer to the real causal effect, though adjusting for income alone doesn't eliminate all confounding." class="img-center" width="95%" >}}

The gap shrinks when we adjust for income. It doesn't disappear, partly because there's a real causal effect and partly because income alone doesn't account for all the confounding in our DAG. To fully block the backdoor paths, we'd also need to adjust for motivation and GPA. But the pattern is clear. Much of what looked like a treatment effect in the raw data was actually selection.

### The Three Rules

The backdoor adjustment works when you can measure enough confounders to block every backdoor path. But sometimes you can't. The critical confounder might be unmeasured, or the only available variables might introduce new biases when you condition on them. The do-calculus provides three rules that handle these harder cases. Together, they cover every situation. If a causal effect can be identified from observational data at all, these three rules can get you there.

Each rule answers one question: when can you simplify a causal expression?

**Rule 1: Drop irrelevant variables.** If a variable doesn't add information about the outcome beyond what you're already accounting for, you can ignore it. Suppose you're already adjusting for family income. A variable like "owns a test prep workbook" is mostly a proxy for income. If it tells you nothing new about SAT scores once you know income, Rule 1 says you can leave it out. Formally, it lets you insert or remove observed variables from a causal expression when they're conditionally independent of the outcome.

**Rule 2: When observing is as good as intervening.** This is the big one. It says that under certain conditions, you can replace a $\text{do}$ with ordinary conditioning. In the SAT example, if you adjust for income, motivation, and GPA, then comparing students who *chose* prep to those who didn't gives you the same answer as an experiment would have. The self-selection is neutralized, so the observational comparison becomes a valid stand-in for the interventional one. This is the rule behind every regression adjustment and matching estimator. Every time you "control for confounders" and interpret the result causally, you're relying on Rule 2.

**Rule 3: You can drop interventions that don't matter.** If you've blocked every path through which a treatment could affect the outcome, then intervening on that treatment changes nothing. You can remove the $\text{do}$ entirely. This sounds almost trivial on its own, but it's essential for multi-step derivations where you need to peel away interventions one at a time.

{{% notation-box %}}

**The Three Rules of Do-Calculus**

Given a DAG $G$, an intervention $\text{do}(X)$, and observed variables $Y$, $Z$, $W$:

**Rule 1** (Insertion/deletion of observations):
$$P(Y \mid \text{do}(X), Z, W) = P(Y \mid \text{do}(X), W) \quad \text{if } Y \perp\!\!\!\perp Z \mid X, W \text{ in } G_{\overline{X}}$$

**Rule 2** (Action/observation exchange):
$$P(Y \mid \text{do}(X), \text{do}(Z), W) = P(Y \mid \text{do}(X), Z, W) \quad \text{if } Y \perp\!\!\!\perp Z \mid X, W \text{ in } G_{\overline{X}\underline{Z}}$$

**Rule 3** (Insertion/deletion of actions):
$$P(Y \mid \text{do}(X), \text{do}(Z), W) = P(Y \mid \text{do}(X), W) \quad \text{if } Y \perp\!\!\!\perp Z \mid X, W \text{ in } G_{\overline{X}\overline{Z(S)}}$$

$G_{\overline{X}}$ is $G$ with incoming arrows to $X$ removed. $G_{\underline{Z}}$ is $G$ with outgoing arrows from $Z$ removed. $Z(S)$ is the set of $Z$ nodes that are not ancestors of any $W$ node in $G_{\overline{X}}$.

{{% /notation-box %}}

The formal notation captures exactly when each simplification is valid, stated in terms of conditional independence in modified versions of the graph. Note that the rules above are stated in their general form, with multiple interventions ($\text{do}(X)$ and $\text{do}(Z)$) already in play. The plain-language descriptions illustrate the most common special case, where you have a single intervention and want to convert it to something you can estimate from data.

[THIS IS STILL TO ABSTRACT]
The real power of these rules comes from chaining them. Start with a causal quantity you want to estimate (something with a $\text{do}$ in it). Apply the rules repeatedly, simplifying step by step, until every $\text{do}$ is gone and the expression contains only things you can compute from data. If you get there, the causal effect is *identified*, meaning it can be computed entirely from the data you have. If you can't eliminate all the $\text{do}$ operators no matter what sequence of rules you try, the effect isn't identifiable. The do-calculus doesn't just give you tools. It tells you when those tools aren't enough.

### When Backdoor Fails

The three rules become important when the backdoor criterion falls apart.

Academic motivation is unmeasurable. We have data on family income, school quality, and GPA, but motivation is an internal disposition that no survey or metric captures reliably. Since motivation affects both whether a student takes prep and how well they score, there's a backdoor path we can't block. The standard adjustment formula won't work because we can't condition on a variable we haven't measured.

But suppose we *can* observe how many hours each student studied. Prep courses increase study time, and study time improves scores. If the entire causal effect of prep on SAT scores flows through hours studied, with no shortcut that bypasses it, we have what's called a front-door path.

{{< figure src="/img/posts/do-calculus/frontdoor-dag.svg" caption="The front-door setup. Motivation confounds Prep Course and SAT Score (dashed arrows), but the causal effect flows entirely through Hours Studied." class="img-center" width="67%" >}}

The front-door criterion works by breaking the problem into two pieces that are each easier to handle.

**Piece one: the effect of Prep on Hours Studied.** Motivation makes some students more likely to take prep, and motivation also makes them study more. But in this DAG, motivation doesn't affect hours studied through any path that doesn't go through Prep Course. So the observed relationship between prep and hours is clean. Students who take the course study about 11 more hours on average, and that difference reflects a genuine causal effect. No adjustment needed.

This relies on a strong assumption: that motivation affects study hours *only* through the decision to take prep, with no direct arrow from Motivation to Hours Studied. If motivated students also study more on their own regardless of the course, the front-door criterion breaks down. The point here is to show how the criterion works when its conditions hold, not to argue that this particular DAG is the right one for SAT prep.

**Piece two: the effect of Hours Studied on SAT Score.** This one is trickier, because motivation affects both hours and scores directly. But we can block that backdoor by adjusting for Prep Course. Among students who all took prep (or all didn't), the variation in hours studied is no longer driven by the choice to take prep. Within those groups, the relationship between hours and SAT scores reflects the causal effect of studying.

Chain the two pieces together. Prep adds 11 hours of study. Each additional hour adds some number of SAT points (estimated from piece two). Multiply them and you have the causal effect of prep on SAT scores, without ever measuring motivation. The logic runs in a single line: Prep → +11 hours → +X points per hour → causal effect.

{{% notation-box %}}

**The Front-Door Formula**

$$P(Y \mid \text{do}(X)) = \sum_m P(M = m \mid X) \sum_x P(Y \mid M = m, X = x) \, P(X = x)$$

where $M$ is the mediator (Hours Studied), $X$ is the treatment (Prep Course), and $Y$ is the outcome (SAT Score). This is more complex than the backdoor formula, and that's expected. The nesting comes from handling the two pieces separately. The first sum captures the effect of treatment on the mediator. The second is itself a backdoor adjustment: it estimates $P(Y \mid \text{do}(M=m))$ by adjusting for $X$, which blocks the confounding path between Hours Studied and SAT Score through motivation.

{{% /notation-box %}}

{{< figure src="/img/posts/do-calculus/frontdoor-estimation.svg" caption="The front-door estimation in three steps. <strong>Left:</strong> Prep courses increase hours studied by about 11 hours. <strong>Center:</strong> Within each prep group, more hours studied predicts higher SAT scores. <strong>Right:</strong> Chaining these effects yields a front-door causal estimate (blue) much smaller than the naive comparison (red dashed), which is inflated by confounding." class="img-center" width="100%" >}}

This entire derivation comes from the do-calculus rules. Rule 2 converts the intervention on Prep into ordinary conditioning for the first piece. Rules 2 and 3 together handle the second piece by adjusting for Prep to block the backdoor through motivation. The derivation is mechanical once you have the right graph. The hard part was drawing the graph correctly: knowing that motivation is a confounder, that hours mediates the effect, and that there's no direct shortcut from prep to SAT scores that bypasses study time.

Those are claims about how SAT preparation actually works, not about statistics.

### The Graph Carries the Knowledge

Do-calculus makes the DAG framework operational. You encode your understanding of how variables relate in a graph, and the calculus tells you whether your causal question is answerable. If it is, the rules derive the exact formula. If it isn't, they tell you that too, and no amount of statistical sophistication will change the answer. This completeness result, proven independently by Huang and Valtorta and by Shpitser and Pearl a decade after the original rules were proposed, is the deep contribution. Earlier methods could identify some causal effects, but they had no way to tell you when identification was impossible. You might try one approach, fail, and never know whether a different approach would have worked or whether the problem was fundamentally unanswerable. The do-calculus settles the question. You're not guessing at identification strategies or hoping your regression is "controlling for the right things." You have a systematic procedure that either works or proves that it can't.

But the calculus is only as good as the graph you give it. Draw the wrong DAG, miss a confounder, get an arrow backwards, and the derived formula will be wrong. The rules guarantee logical consistency given your assumptions. They can't tell you whether your assumptions are right. That still requires understanding the domain, the same point we've been making since the [first post](/post/causal-inference-is-easy/). The do-calculus carries the logic. The graph carries the knowledge. Neither works without the other.


----
##### References

Pearl, J. (1995). Causal diagrams for empirical research. *Biometrika*, *82*(4), 669-688.

Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.

Pearl, J. (2012). The do-calculus revisited. *Proceedings of the 28th Conference on Uncertainty in Artificial Intelligence (UAI)*, 3-11.

Glymour, M., Pearl, J., & Jewell, N. P. (2016). *Causal Inference in Statistics: A Primer*. Wiley.

Huang, Y., & Valtorta, M. (2006). Pearl's calculus of intervention is complete. *Proceedings of the 22nd Conference on Uncertainty in Artificial Intelligence (UAI)*, 217-224.

Shpitser, I., & Pearl, J. (2006). Identification of joint interventional distributions in recursive semi-Markovian causal models. *Proceedings of the 21st National Conference on Artificial Intelligence (AAAI)*, 1219-1226.
