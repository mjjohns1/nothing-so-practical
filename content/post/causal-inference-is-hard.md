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

The difficulty stems from the fact that rival explanations can be hard to identify, hard to measure, and hard to design around. Overlook a confound, measure it poorly, or use an inadequate study design and causal inference fails, regardless of how sophisticated the statistical methods are. These challenges are most apparent when dealing with observational data. However, experiments are also susceptible to these problems. Let's see what this looks like in practice.

### Rock Me Amadeus

A 1993 study had college students listen to a Mozart sonata, a relaxation tape, or silence, then take a spatial reasoning test. The same students rotated through all three conditions. Those who listened to Mozart scored modestly higher, though the effect lasted only about 15 minutes.[^1] The media ran with it. Headlines announced that Mozart makes you smarter. Infant Mozart CDs flooded the market, and several states passed legislation encouraging music in schools.

Subsequent research suggested the excitement was premature. Sitting in silence is boring and slightly fatiguing. Listening to engaging music is stimulating and pleasant. The conditions in the original study differed not only in the presence of Mozart but also in arousal and mood. Follow-up studies found that other enjoyable stimuli, a Schubert piece, a Stephen King story, produced similar boosts, and that the effect disappeared when researchers controlled for arousal and mood.[^2] The active ingredient appears to have been a pleasant, stimulating experience, not Mozart specifically.

Though experiments are one of the best ways to prevent alternative explanations they are not foolproof. The Mozart effect was likely the product of a confound baked into the experimental design. These sorts of conceptual confounds are common and not always easy to notice. Most data scientists, however, don't run psychology experiments. They work with observational data, where they control nothing about how people end up in different groups. If a confound can hide inside a controlled experiment, what happens when we can't control treatment assignment?

### Knowing What to Worry About

The HRT example from the [first post](/post/causal-inference-is-easy/) made selection bias look manageable. Health consciousness affects both treatment choice and heart disease risk. Measure it, control it, move on. But selection is just the most obvious threat. Confounding can arise in multiple ways. Let's say we were able to measure and control for all the covariates responsible for selection. Are we in the clear? Not necessarily.

Many HRT studies took place over years. External events might have affected the two groups differently over that time. Imagine the American Medical Association updated dietary guidelines midway through the study, promoting vegetarian diets specifically for women on HRT. If that policy ends up reducing cardiovascular risk among women already taking HRT, then accounting for baseline selection wouldn't be enough. The groups differed not because of HRT, but because of an outside event that affected them differently. This is a history effect.

Groups selected differently at baseline might also change at different rates over time, regardless of treatment. A tutoring program assigned to struggling students might appear effective simply because they'll tend to drift back toward the average. Regression to the mean is pernicious when one group is selected because they scored at the extreme of some measure. Similarly, if the outcome is measured differently across groups in systematic ways, what looks like a treatment effect might just be a measurement artifact.

{{< notation-box >}}
<p style="margin: 0 0 0.25rem; font-weight: 600;">A (partial) Inventory of Threats to Validity:</p>
<ul style="margin: 0; padding-left: 1.2rem; list-style: none;">
<li><strong>Selection</strong> Groups differ before treatment starts. Health-conscious women choose HRT; any outcome difference may reflect who they are, not what they took.</li>
<li><strong>History</strong> An outside event affects the groups differently mid-study. Dietary guidelines change, and only HRT users follow them.</li>
<li><strong>Maturation</strong> Groups change at different rates on their own. Younger patients recover faster regardless of treatment.</li>
<li><strong>Regression to the mean</strong> Groups selected at extreme values drift back toward the average. Struggling students improve whether or not they're tutored.</li>
<li><strong>Instrumentation</strong> The measurement itself shifts. A hospital upgrades its cardiac screening, catching more events in one group than the other.</li>
</ul>
{{< /notation-box >}}

Not every difference between groups threatens validity. It only matters if the difference could *plausibly* produce results that mimic a causal effect. Consider the tutoring program example. If treatment and control groups have different hair color distributions, that's irrelevant. Hair color doesn't affect academic performance. But if students being tutored are also taking easier classes, that's a real threat. The question isn't whether the groups are different. They almost always are. The question is whether they are different in ways that could generate the observed pattern. No framework can answer that for you.

### Measuring the Weight of Smoke

Identifying the most plausible confounds is only the start. You also have to measure them well enough to actually control for them.

What is "health consciousness" exactly? You could ask people to rate how important their health is. But how many people would endorse the idea that they don't care about their health? You could use behavioral proxies, like gym memberships, vitamin purchases, or preventive care visits. But gym memberships and vitamin purchases are confounded with income, and preventive care visits depend on insurance coverage and access to healthcare.

Maybe you build a composite index combining multiple indicators. But which indicators? How do you weight them? Each choice makes assumptions about what the construct really is. If your measure doesn't capture what matters for both HRT use and cardiovascular disease, controlling for it doesn't eliminate the confounding. It just leaves residual confounding in your estimate.

This is a general problem, not an HRT-specific one. Many of the variables that matter most for causal inference are abstract constructs. Motivation, risk tolerance, management quality, organizational culture. We give them names as if they were things we could put on a scale, but translating them into numbers that capture what actually drives selection and outcomes is a different challenge entirely.

The statistical frameworks require that you've measured all the confounders, not just some of them. If health consciousness has three dimensions and you only capture two, the unmeasured dimension still confounds your result. Your carefully matched samples are still not comparable in the ways that matter.

### Design Around What You Can't Measure

So how do you make valid causal claims when you can't randomize and can't perfectly measure every confounder? Not by hoping your statistical adjustments worked. By designing comparisons that make specific rival explanations implausible. Instead of assuming you've measured everything and adjusting for it, you build your study so that certain confounds *can't* explain the pattern of results. The threats aren't assumed away. They're ruled out by the structure of the comparison.

Difference-in-differences illustrates the logic. Instead of comparing HRT users to non-users at a single point in time (which conflates the treatment effect with all the ways these groups differ), you compare *changes* over time. If health-conscious women are consistently more likely to use HRT, that baseline difference is present in every time period. By looking at whether the *trend* in cardiovascular outcomes shifted after HRT adoption, rather than whether HRT users simply have better outcomes, you neutralize any confounder that remains stable over time. Even unmeasured ones. The design handles what your measurement can't.

{{< figure src="/img/posts/causal-inference/did-hrt.svg" caption="Stylized illustration of a difference-in-differences design. Data are simulated for explanatory purposes and do not represent actual HRT study results." class="img-center" >}}

This doesn't make causal inference easy. It trades one assumption for another. Instead of "I've measured everything correctly," the assumption becomes "treated and untreated groups would have followed the same trend without the treatment." That's a narrower, more defensible claim, and one where domain expertise can do real work. But it's still an assumption, and it can still be wrong. If something other than HRT caused cardiovascular trends to diverge between the groups, the estimate is biased. The design shifts the burden from measurement to plausibility. It doesn't eliminate it.

#### Free Bird

Even sophisticated methods can't save you from a misidentified treatment. Hours after Elon Musk closed his acquisition of Twitter, he tweeted "the bird is freed." Molak [used this event](https://medium.com/data-science/causal-python-elon-musks-tweet-our-googling-habits-bayesian-synthetic-control-187114fc4aa8) to demonstrate how synthetic control, another quasi-experimental method, can estimate causal effects from observational data. Using Google searches for LinkedIn, TikTok, and Instagram as controls, the model estimated a large effect of Musk's tweet on searches for "Twitter."

![Google search interest for "Twitter" was already surging days before the tweet, driven by acquisition news coverage](/img/posts/causal-inference/freebird-trends.svg)

Clean application of a cutting-edge tool. But as the author correctly notes, the outcome "might be influenced not only by Musk's tweet but also by other factors (e.g. media publications on Twitter acquisition)." Musk's acquisition of Twitter and the tweet aren't independent events. The acquisition dominated the news cycle for days before the tweet went out. People were already searching for "Twitter" because of the takeover, not because of one tweet. The treatment and the confounder are entangled.

The synthetic control framework worked exactly as designed. The counterfactual was well-constructed. But no method, however sophisticated, can tell you that your treatment variable is confounded with a concurrent event. That requires understanding the context, the news cycle, the timeline. The method got the math right and the question wrong.

## Still Easy, Still Hard

Causal inference is easy to understand. Eliminate alternative explanations. The frameworks, whether DAGs or potential outcomes, formalize this task. But doing it well requires knowing what the alternatives are, measuring the variables behind them, and designing studies that make specific threats implausible when measurement falls short.

Causal claims from observational data often fail to replicate. Not because researchers lack sophistication, but because the world resists our attempts to isolate single causes. Reasonable people will disagree about whether a given threat has been adequately ruled out, and that disagreement is the point. Causal inference is easy to understand and hard to do well. Not because the math is complicated, but because the world is complicated and our knowledge of it is always incomplete.

[^1]: Rauscher, Shaw & Ky (1993). Music and spatial task performance. *Nature*, 365, 611.

[^2]: Nantais & Schellenberg (1999). The Mozart effect: An artifact of preference. *Psychological Science*, 10(4), 370-373; Thompson, Schellenberg & Husain (2001). Arousal, mood, and the Mozart effect. *Psychological Science*, 12(3), 248-251.
