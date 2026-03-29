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

The $\text{do}$ operator sits at the heart of Pearl's causal framework. The so-called do-calculus that is built around it makes DAGs useful beyond merely visualizing the data generating process. It provides a set of rules for determining when a causal question can be answered with observational data. The rules cover situations the backdoor criterion can't handle, and they work on any DAG. Let's look at an example to make this concrete.

Suppose a university wants to know whether taking an SAT prep course improves scores on the test. Students self-select into the course, and the kind of student who signs up for test prep isn't a random draw from the population. The university has data on about 5,000 students. The naive comparison shows that students who took the prep course scored 140 points higher on average. But nobody should believe that number without asking what else might explain it.

### Seeing vs. Doing

Look at the 140-point gap and think about what it actually tells you. It answers a narrow question. Among students who *happened to take* the prep course, what were their average scores compared to students who didn't? That's a fact about the data. It's not wrong. But it doesn't tell you what would happen if you took a random student and made them take the course.

The students who chose prep are different from those who didn't, in ways that also affect their SAT scores. They tend to come from wealthier families that can afford the course. They tend to be more motivated. They tend to have stronger academic records. All of these boost SAT scores independently of any prep course. So the 140-point gap reflects the real effect of prep *plus* all the ways that prep-takers were already going to outscore everyone else.

In notation, the gap is $E[\text{SAT} \mid \text{Prep} = 1] - E[\text{SAT} \mid \text{Prep} = 0]$. Read the vertical bar as "given that" and the expression as "the average SAT score among students where Prep equals 1 (took the course)." It's a comparison conditioned on what we *observe*. The causal question needs something different: $E[\text{SAT} \mid \text{do}(\text{Prep} = 1)]$. The $\text{do}$ means we're not looking at who chose prep. We're asking what would happen if we *assigned* it, overriding all the reasons students normally select into the course.

Think of it this way. Observing is watching the system run naturally and noting what happens. Doing is reaching in and changing something yourself. When you observe who takes prep, you see a mix of the course's effect and the characteristics of the people who chose it. When you *do* prep (assign it randomly), you break that link. The students' backgrounds still affect their scores, but those backgrounds no longer determine who got the course. Any remaining difference between the prep group and the non-prep group must come from the prep itself.

A DAG makes the contamination visible.

{{< figure src="/img/posts/do-calculus/sat-dag.svg" caption="A directed acyclic graph for the SAT prep example. Each arrow represents a direct causal relationship. Red arrows trace confounding paths. The dashed blue arrow is the causal effect we want to estimate." class="img-center" >}}

Each arrow is a claim about what causes what. Parents' education shapes both family income and motivation. Family income determines access to prep courses and school quality. School quality influences GPA, motivation, and SAT scores directly. Motivation drives students to sign up for prep, to study harder, and feeds into their GPA. GPA predicts both willingness to invest in prep and performance on the SAT.

All of these connections create paths from Prep Course to SAT Score that have nothing to do with prep actually working. Trace one out. Family Income → Prep Course is one arrow, and Family Income → School Quality → SAT Score is another chain. A student from a wealthy family is more likely to take prep *and* more likely to attend a school that boosts their SAT score. That path inflates the naive comparison even if prep does nothing. Or trace Motivation → Prep Course alongside Motivation → SAT Score. Motivated students sign up for prep *and* score higher regardless. Another path that makes prep look effective when it might not be.

These are what's called backdoor paths, and they're the reason the naive comparison is inflated.

Now look at what happens when we apply the $\text{do}$ operator. Graphically, $\text{do}(\text{Prep})$ means we delete every arrow pointing *into* the Prep Course node. We're saying: forget about why students normally take prep. We're setting it ourselves.

{{< figure src="/img/posts/do-calculus/sat-dag-do.svg" caption="The graph under do(Prep), known in the literature as the 'mutilated graph.' Arrows into Prep Course have been severed (gray dashed), breaking every backdoor path. The highlighted node is now set externally rather than determined by confounders." class="img-center" >}}

In this modified graph, Prep Course has no parents. Nothing causes it. It's as if we flipped a coin. The confounders still exist and still affect SAT scores, but they no longer determine who takes prep. Any association between Prep and SAT Score that survives in this graph has to flow through the causal arrow. That's exactly the quantity $P(\text{SAT} \mid \text{do}(\text{Prep}))$ represents.

### The Adjustment Formula

Of course, we can't actually delete arrows in the real world. We didn't run an experiment. But under the right conditions, we can use the data we have to compute what the experiment *would* have shown. The most common way to do this is the backdoor adjustment formula.

The idea is stratification. Instead of comparing all prep-takers to all non-takers (which is contaminated by confounding), compare them *within groups that share the same background*. Among low-income students, how much higher do prep-takers score? Among middle-income students? Among high-income students? If you compute the prep effect within each group and then average those effects together, weighted by how common each group is in the population, the confounding washes out. What's left is the causal effect.

{{% notation-box %}}

**The Backdoor Adjustment Formula**

$$P(Y \mid \text{do}(X)) = \sum_z P(Y \mid X, Z=z) \, P(Z=z)$$

In words: to estimate what would happen if we *assigned* the treatment, look at the outcome among people with the same confounder values ($Z = z$), then average across all confounder values weighted by how common they are in the full population. $Z$ must block all backdoor paths from $X$ to $Y$ and must not include anything caused by the treatment.

{{% /notation-box %}}

A quick example makes this concrete. Suppose 40% of students are low-income and 60% are high-income. Among low-income students, prep-takers scored 30 points higher than non-takers. Among high-income students, the difference is 25 points. The adjusted causal effect is $0.4 \times 30 + 0.6 \times 25 = 27$ points. That's a weighted average of the within-group effects, where the weights reflect how common each group is in the *full population*, not among prep-takers.

The weighting by $P(Z=z)$ is what separates this from a simple subgroup analysis. Without it, you'd over-represent the confounder profiles most common among the treated group, which is the selection bias you're trying to eliminate. The population weights put everyone on equal footing.

{{< figure src="/img/posts/do-calculus/confounded-vs-adjusted.svg" caption="<strong>Left:</strong> The naive comparison shows a large gap between prep and no-prep students. <strong>Right:</strong> After stratifying by income, the within-stratum differences shrink substantially. The remaining gap is closer to the real causal effect, though adjusting for income alone doesn't eliminate all confounding." class="img-center" width="95%" >}}

The gap shrinks when we adjust for income. It doesn't disappear, partly because there's a real causal effect and partly because income alone doesn't account for all the confounding in our DAG. To fully block the backdoor paths, we'd also need to adjust for motivation, GPA, and school quality. But the pattern is clear. Much of what looked like a treatment effect in the raw data was actually selection.

### The Three Rules

The backdoor adjustment works when you can measure enough confounders to block every backdoor path. But sometimes you can't. The critical confounder might be unmeasured, or the only available variables might introduce new biases when you condition on them. The do-calculus provides three rules that handle these harder cases. Together, they cover every situation. If a causal effect can be identified from observational data at all, these three rules can get you there.

Each rule answers one question: when can you simplify a causal expression? The plain-language descriptions below are what matter for understanding. The formal notation box that follows is reference material for when you need to verify a specific identification strategy. You don't need to memorize it to follow the rest of the article.

**Rule 1: You can drop irrelevant variables.** If a variable doesn't add information about the outcome beyond what you're already accounting for, you can ignore it. Suppose you're already adjusting for family income in the SAT example. A variable like "owns a test prep workbook" is mostly a proxy for income. If it tells you nothing new about SAT scores once you know income, Rule 1 says you can leave it out. Formally, it lets you insert or remove observed variables from a causal expression when they're conditionally independent of the outcome.

**Rule 2: Sometimes observing is as good as intervening.** This is the big one. It says that under certain conditions, you can replace a $\text{do}$ with ordinary conditioning. In the SAT example, if you adjust for income, motivation, and GPA, then comparing students who *chose* prep to those who didn't gives you the same answer as an experiment would have. The self-selection is neutralized, so the observational comparison becomes a valid stand-in for the interventional one. This is the rule behind every regression adjustment and matching estimator. Every time you "control for confounders" and interpret the result causally, you're relying on Rule 2.

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

The real power of these rules comes from chaining them. Start with a causal quantity you want to estimate (something with a $\text{do}$ in it). Apply the rules repeatedly, simplifying step by step, until every $\text{do}$ is gone and the expression contains only things you can compute from data. If you get there, the causal effect is *identified*, meaning it can be computed entirely from the data you have. If you can't eliminate all the $\text{do}$ operators no matter what sequence of rules you try, the effect isn't identifiable. The do-calculus doesn't just give you tools. It tells you when those tools aren't enough.

### When Backdoor Fails

The three rules earn their keep when the backdoor criterion falls apart. Let's modify the SAT example to see how.

Suppose motivation is unmeasurable. We have data on family income, school quality, and GPA, but motivation is an internal disposition that no survey captures reliably. Since motivation affects both whether a student takes prep and how well they score, there's a backdoor path we can't block. The standard adjustment formula won't work because we can't condition on a variable we haven't measured.

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
