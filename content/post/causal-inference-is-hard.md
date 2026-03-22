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

The [first post](/post/causal-inference-is-easy/) argued that causal inference is just a matter of ruling out rival explanations. That sounds straightforward. Why is it often so difficult in practice? Why did observational studies on hormone replacement therapy (HRT) get it so wrong? Why do causal claims from observational data so often fail to replicate?

The difficulty stems from fact that rival explanations can be hard to identify, hard to measure, and hard to design away. Overlook a confound, measure it poorly or use an inadequate study design and causal inference fails, regardless of how sophisticated the statistical methods are. These challenges are most apparent when dealing with observational data. However, experiments are also susceptible to these problems. To see how difficult it can be to rule out alternative explanations in practice, it's instructive to first look at a case when randomization was not sufficient to eliminate confounding.

### Rock Me Amadeus

A 1993 study found that college students who listened to Mozart for 10 minutes outperformed students who sat in silence on a spatial reasoning task. The finding was interpreted as evidence that Mozart's music specifically enhances cognitive ability. It spawned a cultural phenomenon, infant Mozart CDs, and even state legislation encouraging music in schools.

Subsequent research suggested the excitment over this study might have been premature. Sitting in silence is boring and slightly fatiguing. Listening to engaging music is stimulating and pleasant. The two conditions differed not only in the presence of Mozart but also arousal and mood. When students were exposed to an equally engaging but non-musical stimulus, like a Stephen King audiobook or a piece by Philip Glass, the performacne boost disappeared. It seems the active ingredient was a pleasan feeling, not Mozart.

Though experiments are one of the best ways to deal with confounds they are not fullproof. The Mozart effect was the product of a confound baked into the experimental design. These sorts of procedural confounds are common and not always easy to notice. Most data scientists don't run psychology experiments, though. They work with observational data, where they control nothing about how people end up in different groups. If a confound can hide inside a controlled experiment, what happens when we can't control treatment assignment?

### Knowing What to Worry About

The HRT example from the [first post](/post/causal-inference-is-easy/) made selection bias look manageable. Health consciousness affects both treatment choice and heart disease risk. Measure it, control it, move on. But selection is just the most obvious threat. Confounding can arise in multiple ways. Let's say we were able to measure and control for all the covariates responsible for selection. Are we in the clear? Not necessarily.

Many HRT studies took place over years. We need to consider the possibility that external events differentially affected the treatment and control groups in that time. Imagine the American Medical Association updated dietary guidelines midway through the study, promoting vegetarian diets specifically for women on HRT. If that policy ends up reducing cardiovascular risk among women already taking HRT, then accounting for baseline selection wouldn't be enough. The groups differed not because of HRT, but because of an outside event affected them differently. This is referred to as a history effect.

Groups selected differently at baseline might also change at different rates over time, regardless of treatment. A tutoring program assigned to struggling students might appear effective simply because those students were going to improve anyway, just more slowly than their higher-performing peers. The groups were maturing at different rates, and that differential trajectory mimics a treatment effect. This is a maturation effect.

Similarly, if the outcome is measured differently across groups, in systematic ways, what looks like a treatment effect might just be a measurement artifact. And if one group was selected because they scored at the extreme end of some measure, they'll tend to drift back toward the average on their own. This regression toward the mean can look a lot like a treatment effect if you're not watching for it. This is an instrumentation effect.

Not every difference between groups threatens validity. The difference only matters if it could *plausibly* produce results that mimic your causal effect. Consider a study on whether tutoring improves math scores. If treatment and control groups differ in hair color distribution, that's irrelevant. Hair color doesn't affect math performance. But if they differ in prior math achievement, that's a real threat. The question isn't "are the groups different?" They almost always are. The question is "are they different in ways that could generate the pattern I observe?" No framework can answer that for you.

#### Free Bird

The day after Elon Musk became Twitter CEO, he tweeted "the bird is freed." Molak [used this event](https://medium.com/data-science/causal-python-elon-musks-tweet-our-googling-habits-bayesian-synthetic-control-187114fc4aa8) to demonstrate how synthetic control can estimate the causal effect of that tweet on Google searches for "Twitter." Synthetic control builds a counterfactual by weighting similar units that weren't exposed to the treatment. Using searches for LinkedIn, TikTok, and Instagram as controls, the model produced a large effect.

This seems like a clean application of a modern causal inference tool. But as the author correctly notes, the outcome "might be influenced not only by Musk's tweet but also by other factors (e.g. media publications on Twitter acquisition)." The confound is subtle. Musk's acquisition of Twitter and the tweet aren't independent events. The acquisition dominated the news cycle for days before the tweet went out. People were already searching for "Twitter" because of the acquisition, not because of one tweet. The treatment and the confounder are entangled. You can't separate their effects.

The synthetic control framework worked as designed. The counterfactual was well-constructed. But no framework can tell you that your treatment variable is confounded with a concurrent event. That requires understanding the context, the news cycle, the timeline.

### Measuring the Weight of Smoke

Identifying the most plausible confounds is only half the problem. You also have to measure them well enough to actually control for them.

What is "health consciousness" exactly? You could ask people to rate how important their health is. But how many people would endorse the idea that they don't care about their health? You could use behavioral proxies, like gym memberships, vitamin purchases, or preventive care visits. But gym memberships and vitamin purchases are confounded with income, and preventive care visits depend on insurance coverage and access to healthcare.

Maybe you build a composite index combining multiple indicators. But which indicators? How do you weight them? Each choice makes assumptions about what the construct really is. If your measure doesn't capture what matters for both HRT use and cardiovascular disease, controlling for it doesn't eliminate the confounding. It just adds noise to your model.

This is a general problem, not an HRT-specific one. Many of the variables that matter most for causal inference are abstract constructs. Motivation, risk tolerance, management quality, organizational culture. We give them names as if they were things we could put on a scale, but translating them into numbers that capture what actually drives selection and outcomes is a different challenge entirely.

The statistical frameworks require that you've measured all the confounders, not just some of them. Partial control isn't enough. If health consciousness has three dimensions and you only capture two, the unmeasured dimension still confounds your result. Your carefully matched samples are still not comparable in the ways that matter.

### Design Around What You Can't Measure

So how do you make valid causal claims when you can't randomize and can't perfectly measure every confounder? Not by hoping your statistical adjustments worked. By designing comparisons that make specific rival explanations implausible. Instead of assuming you've measured everything and adjusting for it, you build your study so that certain confounds *can't* explain the pattern of results. The threats aren't assumed away. They're ruled out by the structure of the comparison.

Difference-in-differences illustrates the logic. Instead of comparing HRT users to non-users at a single point in time (which conflates the treatment effect with all the ways these groups differ), you compare *changes* over time. If health-conscious women are consistently more likely to use HRT, that baseline difference is present in every time period. By looking at whether the *trend* in cardiovascular outcomes shifted after HRT adoption, rather than whether HRT users simply have better outcomes, you neutralize any confounder that remains stable over time. Even unmeasured ones. The design handles what your measurement can't.

Other quasi-experimental methods follow the same basic logic. Regression discontinuity exploits arbitrary cutoffs. If a policy applies to everyone above some threshold (age, test score, income) and not to those just below, people near the cutoff are almost identical except for their treatment status. The cutoff creates a local experiment where confounders are balanced, not because you measured them, but because people just above and just below the line are effectively the same. Instrumental variables work by finding a source of variation in treatment that's unrelated to the confounders. If you can identify something that affects whether someone gets treated but has no direct effect on the outcome, you can use that variation to isolate the causal effect, sidestepping the confounders entirely.

Each of these designs makes a different set of rival explanations implausible. None eliminates all of them. Difference-in-differences handles time-invariant confounders but assumes that treated and untreated groups would have followed parallel trends without the treatment. Regression discontinuity gives you clean causal estimates, but only for people near the cutoff, who might not be representative of the broader population. Instrumental variables require an instrument that's both relevant and truly unrelated to the outcome through other channels, an assumption that's often hard to defend.

The design approach doesn't make causal inference easy. But it shifts the burden from "did I measure everything correctly?" to "is this specific assumption plausible?" That's a more tractable question, and one where domain expertise, theory, and supplementary evidence can do real work.

## Still Easy, Still Hard

Causal inference is easy to understand. Eliminate alternative explanations. The frameworks, whether DAGs or potential outcomes, formalize this task. But doing it well requires knowing what the alternatives are, measuring the variables behind them, and designing studies that make specific threats implausible when measurement falls short.

This isn't a checklist where you tick boxes and declare victory. It's an ongoing argument. Are the threats plausible? Have they been adequately ruled out? Could there be confounds we haven't considered? Different researchers will answer differently based on their knowledge of the domain and their reading of the evidence.

Causal claims from observational data often fail to replicate. Not because researchers lack sophistication, but because the world resists our attempts to isolate single causes. Causal inference is easy to understand and hard to do well. Not because the math is complicated, but because the world is complicated and our knowledge of it is always incomplete.

[^1]: Rauscher, Shaw & Ky (1993). Music and spatial task performance. *Nature*, 365, 611.

[^2]: Chabris (1999). Prelude or requiem for the "Mozart effect"? *Nature*, 400, 826-827; Steele, Bass & Crook (1999). The mystery of the Mozart effect. *Psychological Science*, 10(4), 366-369.
