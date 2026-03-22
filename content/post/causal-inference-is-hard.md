---
title:       "Causal Inference Is Hard"
subtitle:    "COMING SOON: Part two of a two-part series"
description: "The real reasons that causal inference is hard to pull off in practice"
date:        2026-03-15
author:      "MJ"
image:       ""
tags:        ["causal inference"]
categories:  []
draft:       FALSE
---

## Causal Inference is Hard

The first post argued that casual inference is just a matter of ruling out rival hypotheses. That sounds fairly straightforward. Why, then, is it often so difficult in practice? Why did observational studies on hormone replacement therapy (HRT) get it so wrong? Why do causal claims from observational data often fail to replicate?

Consider the hormone replacement therapy (HRT) example more closely. We specified health consciousness as a confounder that affects both treatment choice and the outcome. Both the potential outcomes framework and the DAG framework tell us we need to measure and control for confounders. Both give us clear instructions on how to proceed.

[preview the argument - identifying potential confounds and measuring them adequately for control is very difficult in practice. Identifying the confounds requires domain expertise. Using study design principles is a better approach to handling confounds that are difficult to measure]

This is all well and good if we know health consciousness is something to worry about and have measured it. But figuring out which variables matter requires understanding all the factors that cause the outcome and the treatment variable. The ability to measure those variables requires solving a completely different set of problems. Get either one wrong and causal inference fails, regardless of how sophisticated your statistical methods are.

Understanding causal inference as the process of eliminating alternative explanations means we need to identify sources of confounding that could undermine the validity of our study. The validity threats framework provides a useful taxonomy to guide how we think about what can go wrong (Shadish, Cook, & Campbell, 2002). [transition sentence here]


## Threats to Validity

Internal validity asks whether the relationship between treatment and outcome is causal. Did X cause Y, or was it something else?

Confounding can arise in multiple ways. In observational studies, selection bias is the most obvious threat. Without random assignment, study groups can end up different for reasons other than the treatment. However, selection is just one of many potential ways confounding can occur. Let's say we were able to measure and control for health consciousness, and all the covariates responsible for selection. Are we in the clear? Not necessarily.

Many HRT studies took place over the course of years. We need to consider the possibility that the women taking HRT were differentially impacted by outside events in that time. For example, imagine the American Medical Association updated their treatment guidelines for HRT in the middle of the study to promote adoption of a vegetarian diet. If that change could plausibly reduce CVD risk only among women on HRT, then accounting for selection isn't sufficient.

This is an example of a history confound. External events during the study differentially affect study groups, creating spurious associations between treatment and outcome. This is just one of many potential confounding patterns, which can be difficult to identify and account for. The number and types of threats can vary depending on the causal question and study design, so spotting them requires knowing where to look.

Selection bias can also interact with other processes, creating particularly insidious confounding patterns:

**Selection × Maturation:** The groups are changing at different rates even without treatment. High-performing students improve faster than low-performing students regardless of the intervention.

**Selection × Instrumentation:** Outcome measurement differs between groups in systematic ways. Maybe the treatment group gets a harder test, or measurements are taken at different times of day, or the scale has ceiling effects for one group.

**Selection × Regression:** One group was selected for being extreme on some measure, so they'll regress toward the mean regardless of treatment.

These interaction effects are especially problematic because they can masquerade as treatment effects even when researchers successfully measure and control for baseline differences between groups.

Not every difference between groups threatens validity. The difference only matters if it could *plausibly* produce results that mimic your causal effect. Consider a study on whether tutoring improves math scores. If treatment and control groups differ in hair color distribution, that's irrelevant. Hair color doesn't affect math performance. But if they differ in prior math achievement, that's a real threat.

The key question is whether this difference could generate the pattern you observe. Maturation only threatens validity if groups mature at different rates AND that differential maturation affects the outcome. History only matters if the external event differentially impacts groups in ways relevant to what you're measuring. This is why domain expertise is essential. Knowing which of these threats is plausible in a specific study requires deep understanding of the factors that can influence the outcome you are studying.

## Hidden Confounds

Even when you understand the types of confounding that can occur, identifying them in real studies requires detective work. Hidden confounds come in different forms. Sometimes the treatment itself is ambiguous, sometimes confounding is baked into the procedures, and sometimes the confounder is conceptually clear but practically impossible to measure. Three examples illustrate these challenges.

### Free Bird

The day after Elon Musk became Twitter CEO he tweeted, "the bird is freed". [Molak](https://medium.com/data-science/causal-python-elon-musks-tweet-our-googling-habits-bayesian-synthetic-control-187114fc4aa8) used this event to demonstrate how synthetic control can be used to estimate the causal effect of that tweet on Google searches for "Twitter". Synthetic control is designed to estimate what would have happened without the intervention (i.e., tweet) using a weighted combination of similar units that weren’t exposed. He built the synthetic control using searches for LinkedIn, TikTok, and Instagram, and found a large effect.

This seems like an ideal situation for a modern causal inference tool like synthetic control. But as Molak correctly points out, "this hypothesis is difficult to verify, as the outcome might be influenced not only by Musk's tweet but also by other factors (e.g. media publications on Twitter acquisition)." The confound is subtle. Musk's acquisition of Twitter and the tweet aren't independent events. The acquisition was major news for days before the tweet. People were already searching for Twitter because of the acquisition news, not necessarily because of one tweet. The tweet and the acquisition are confounded, you can't separate their effects.

### Indulge your Curiosity

Curiosity makes people more indulgent, at least that's the claim of Wiggins et al. in their 2019 study. Participants completed a writing task designed to make them feel curious (or not), then chose between two gym memberships, one standard gym and one "indulgent" with unusual features like a negative-edge pool and Scandinavian sauna.

Participants in the "curious" condition were much more likely to choose the indulgent option. The effect was large and highly significant. From the study description, it appeared the writing task (the curiosity induction) and the gym choice were presented as separate, unrelated tasks. Instead, it turns out, participants in the curiosity condition were explicitly told to be in an exploratory state when choosing a gym.

This is a massive yet hidden confound, discovered only after examining the actual survey materials. Data Colada ran a large replication study, adding a condition that removed the confounded instructions. With the original (confounded) instructions curiosity increased choice of indulgent gym, replicating the original finding. With “clean” instructions ("Please make a decision on the next screen"), curiosity had no impact on gym choice.

Random assignment didn't prevent confounding because the confound was in the experimental procedure itself, hidden in the transition between tasks. The groups didn't differ at baseline, but they received psychologically different instructions that conflated the curiosity induction with demand.

### Measuring the Weight of Smoke

Even when you correctly identify that a confounder matters, you now face the problem of measuring it. What is "health consciousness" exactly? You could ask participants to rate how important their health is. But how many people would actually endorse the idea that they don't care about their health? You could use behavioral proxies, like gym memberships, vitamin purchases, or preventive care visits. But gym memberships and vitamin purchases are confounded with income, and preventive care visits depend on insurance coverage and access to healthcare.

Maybe you build a composite index combining multiple indicators. But which indicators? How do you weight them? Each choice makes assumptions about what the construct really is. If your measure doesn't capture what matters for both HRT use and cardiovascular disease, controlling for it doesn't eliminate the confounding, it just adds noise to your model.

The potential outcomes framework requires conditional independence: treatment assignment must be independent of potential outcomes, conditional on measured covariates. This means you need to measure ALL the confounders, not just some of them. Partial control isn't enough. If health consciousness has three dimensions and you only measure two, the unmeasured dimension still confounds your result. Your carefully matched samples are still not exchangeable.

## The Design Approach

So how do you actually do valid causal inference when you can't randomize? Not by hoping your statistical adjustments worked. By adding design features that make specific threats implausible. This is different from the statistical control approach. You're not assuming you measured all confounders and adjusting for them. You're creating empirical tests that specific threats can't explain the pattern of results. The threats aren't assumed away—they're ruled out by the data.

Modern quasi-experimental methods follow this basic logic. They're embedded designs that make specific confounds implausible using structured comparisons, not just through statistical adjustment. For example, a difference-in-differences design rules out time-invariant confounding by comparing changes over time rather than levels. If health-conscious women are consistently more likely to use HRT throughout the study period, difference-in-differences accounts for this by examining whether the trend in cardiovascular outcomes changed after HRT adoption, not just whether HRT users have different outcomes. The design neutralizes confounders that remain stable over time, even unmeasured ones.

The design approach helps. Adding multiple tests of plausibility makes alternative explanations less tenable. But irreducible challenges remain.

You can't fully check your assumptions. Unmeasured confounding is by definition unmeasured. Counterfactual trends are unobservable. You can test for jumps in observables, but what about unobservables? The best you can do is sensitivity analysis: how large would unmeasured confounding need to be to explain away the effect? This brackets the uncertainty rather than eliminating it. Measurement remains hard—you control for what's available and hope it's adequate. Resources constrain design—perfect designs are rarely feasible, and you make tradeoffs between internal validity, external validity, statistical power, and practical constraints.

## Still Easy, Still Hard

Causal inference is easy to understand: eliminate alternative explanations. The frameworks, whether DAGs or potential outcomes, just formalize this task. But executing requires understanding of the data-generating process, valid measurement of confounders, and clever design features to make threats implausible when you can't measure everything.

The validity threats framework isn't a checklist where you tick boxes and declare victory. It's an ongoing dialogue. Are the threats even plausible? Have they been adequately ruled out? Could there be hidden confounds we haven't considered? Different researchers will answer differently based on their knowledge of the domain and their assessment of the evidence.

This is why causal claims from observational data so often fail to replicate—not because researchers lack sophistication, but because the world resists our attempts to isolate single causes. Causal inference is easy to understand and hard to do well—not because the math is complicated, but because the world is complicated and our knowledge of it is always incomplete.

The Mozart Effect.

The original finding: Rauscher, Shaw & Ky (1993) found that college students who listened to Mozart for 10 minutes outperformed students who sat in silence on a subsequent spatial reasoning task. The paper was widely interpreted as evidence that Mozart's music specifically enhances cognitive ability — it spawned a cultural phenomenon, infant Mozart CDs, and even state legislation encouraging music in schools.

The confound: The two conditions differed not just on "Mozart vs. nothing" but on *arousal and mood*. Sitting in silence is boring and slightly fatiguing; listening to engaging music is stimulating and pleasant. Subsequent researchers showed that the boost disappeared entirely when you used an equally engaging but non-musical stimulus — a Stephen King audiobook, a piece by Philip Glass, or even a passage on relaxation exercises produced the same spatial reasoning bump when participants found those enjoyable. The active ingredient was arousal/mood, not Mozart specifically.

The overturning: Chabris's 1999 meta-analysis and a series of follow-up experiments by Steele, Bass & Crook demonstrated that once you controlled for arousal and enjoyment, there was no residual "Mozart effect." Any engaging stimulus worked equally well.

Elderly priming and walking speed (Bargh et al., 1996\)

Participants who unscrambled sentences containing words associated with old age (bingo, Florida, wrinkled) subsequently walked more slowly down a hallway than controls. This became a flagship result for "behavioral priming" — the idea that concepts, once activated, unconsciously shape motor behavior. When Doyen et al. (2012) replicated the study but added a twist — some experimenters were told to expect slower walking, others weren't — the slow-walking effect only appeared when experimenters *expected* it to. The confound was experimenter expectancy: experimenters who knew the participant had been primed with elderly concepts were subtly and unconsciously influencing participants' gait. The original study had no blind experimenters, so this variable was completely uncontrolled.

Glucose restores willpower (Gailliot et al., 2007\)

A series of studies claimed that consuming a sugary drink after an ego-depleting task restored self-control, supporting a "blood glucose as fuel for willpower" model. The mechanism seemed straightforward: exerting self-control burns glucose, replenishing it recharges you. Molden et al. (2012) then showed that simply *rinsing your mouth* with a glucose solution — without swallowing any — produced the same restoration effect. Since no glucose actually entered the bloodstream, the confound was the sensory/motivational signal of sweetness itself, not blood glucose replenishment. The interesting metabolic story was an artifact of not separating the taste of sugar from its physiological effects.

Violent video games and aggression (Anderson & Dill, 2000 and related work)

Experiments showing that violent video games increased aggressive thoughts and behavior were influential for years. But Przybylski et al. and others pointed out that in most of these studies, the "violent" and "nonviolent" games also differed substantially in **difficulty and frustration level** — violent games were often harder, more competitive, and more punishing. When researchers matched games on frustration and competitiveness while varying only violence content, the aggression effect shrank dramatically or disappeared. The active ingredient appears to have been frustration, not violent content per se — a confound baked into almost every study in the literature because researchers hadn't thought to control for it.

