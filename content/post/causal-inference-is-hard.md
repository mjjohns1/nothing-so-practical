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


The [first post](/post/causal-inference-is-easy/) argued that causal inference is just a matter of ruling out rival explanations. That sounds straightforward. Why is it often so difficult in practice? Why did observational studies on hormone replacement therapy (HRT) get it so wrong? Why do causal claims from observational data so often fail to replicate? It's not for lack of skill or effort.

The difficulty is that rival explanations can be hard to identify, hard to measure, and hard to design around. Overlook a confound, measure it poorly, or choose an inadequate study design and causal inference fails, no matter how sophisticated the DAG or statistical notation. The model will estimate the treatment effect you ask for and produce a clean-looking result. When causal inference fails, it fails silently.

### Rock Me Amadeus

In 1993, researchers at UC Irvine had college students listen to Mozart, a relaxation tape, or silence for 10 minutes then take a spatial reasoning test. Participants scored highest after listening to Mozart.[^1] The media ran with it. Despite the study being designed to test the effects of music on cognition, headlines announced that Mozart makes you smarter. Mozart for babies CDs flooded the market, and several states passed legislation encouraging music in schools.

Sitting in silence is boring and slightly fatiguing. Listening to engaging music is stimulating and pleasant. The conditions in the original study didn't just differ in the presence of Mozart. They also differed in arousal and mood. Follow-up studies found that other enjoyable stimuli (e.g., Schubert, a Stephen King story) produced similar boosts, and that the effect disappeared when researchers controlled for arousal and mood.[^2] The active ingredient seemed to be a stimulating experience, not Mozart.

The confound here wasn't statistical, it was conceptual. Comparing Mozart to silence or relaxation instructions doesn't isolate Mozart. It confounds music with the psychological experience of music itself. Engagement, pleasure, stimulation. No statistical adjustment could have fixed it. The confound was baked into the treatment contrast. The researchers wanted to test the effect of music on spatial reasoning when the comparison actually tested whether an engaging experience outperformed a boring one.

This was a controlled experiment. Participants were randomly assigned to conditions. The researchers did everything right by the standards of experimental design. And they still got the wrong answer. If a confound can hide inside a controlled experiment despite correct execution, what happens when you can't control treatment assignment at all?

### Knowing What to Worry About

The HRT example from the [first post](/post/causal-inference-is-easy/) made selection bias look manageable. Health consciousness affects both treatment choice and heart disease risk. Measure it, control it, move on. But selection is just the most obvious threat. Confounding can enter through the back door in ways that are hard to anticipate.

Many HRT studies took place over years. External events might have affected the groups differently. Imagine the American Medical Association updated dietary guidelines midway through the study, promoting vegetarian diets specifically for women on HRT. If that policy ends up reducing cardiovascular risk among women already taking HRT, then accounting for baseline selection wouldn't be enough. The groups differed not because of HRT, but because of an outside event that affected them differently.

Or consider a tutoring program assigned to struggling students. It might appear effective simply because students selected at the extreme of any measure tend to drift back toward the average. Regression to the mean looks exactly like a treatment effect. Similarly, if a hospital upgrades its cardiac screening procedure partway through a study, catching more events in one group than the other, what looks like a treatment effect might just be a measurement artifact.

These threats don't announce themselves. They hide inside the data-generating process and mimic the pattern you'd expect if the treatment worked. Not every difference between groups is a problem. If treatment and control groups have different hair color distributions, that's irrelevant. Hair color doesn't cause heart disease. But if the groups differ in ways that could *plausibly* produce the pattern of results you observe, you have a rival explanation that no amount of statistical rigor will fix. The question isn't whether the groups are different. They almost always are. The question is whether they are different in ways that could generate the observed result.

Even when the treatment contrast is right and you know what the threats are, you still have to measure them well enough to actually neutralize them.

### Measuring the Weight of Smoke

What is "health consciousness" exactly? You could ask people to rate how important their health is. But how many people would endorse the idea that they don't care about their health? You could use behavioral proxies, like gym memberships, vitamin purchases, or preventive care visits. But gym memberships and vitamin purchases are confounded with income, and preventive care visits depend on insurance coverage and access to healthcare.

Maybe you build a composite index combining multiple indicators. But which indicators? How do you weight them? Each choice makes assumptions about what the construct really is. If your measure doesn't capture what matters for both HRT use and heart disease, controlling for it doesn't eliminate the confounding. It just leaves residual error in your estimate.

This is a general problem, not an HRT-specific one. Many of the variables that matter most for causal inference are abstract constructs like motivation, risk tolerance, management quality, organizational culture. We give them names and put them on a scale, but translating them into numbers that can capture what actually drives selection is a different challenge entirely.

Causal inference frameworks require that you've measured all the confounders, not just some of them. If health consciousness has three dimensions and you only capture two, the unmeasured dimension still confounds your result. The carefully weighted samples are not comparable in the ways that matter.

This is the bind. The variables that matter most for causal inference can be the hardest to measure. If we can't measure them well, we need a strategy that doesn't rely solely on measurement.

### Design Around What You Can't Measure

Design offers one approach to valid causal claims when confounders are hard to quantify. Instead of assuming all confounds have been measured and controlled for, you select a design so that plausible confounds *can't* explain the pattern of results. The threats aren't assumed away. They're ruled out by principled comparisons.

Difference-in-differences illustrates the logic. Instead of comparing HRT users to non-users at a single point in time, we compare *changes* over time. If health-conscious women are consistently more likely to use HRT, that baseline difference is present in every period. By looking at whether the *trend* in cardiovascular outcomes shifted after HRT adoption, you neutralize any confounder that remains stable over time. Even unmeasured ones. The design handles what your measurement can't.

{{< figure src="/img/posts/causal-inference/did-hrt.svg" caption="Stylized illustration of a difference-in-differences design. Data are simulated for explanatory purposes and do not represent actual HRT study results." class="img-center" >}}

This trades one assumption for another. Instead of assuming we measured everything we assume that treated and untreated groups would have followed the same trend without the treatment. That's narrower and more defensible, and it's the kind of claim where domain expertise can do real work. But it can still be wrong in ways that are hard to detect. The parallel trends assumption is untestable in the post-treatment period, exactly where it matters. You can check whether trends were parallel *before* treatment, but that doesn't guarantee they would have stayed parallel afterward. An event that coincides with treatment and differentially affects the groups will bias the estimate, and the model has no way to flag it. The design shifts the burden from measurement to plausibility but it doesn't eliminate it.

#### Free Bird

Even sophisticated methods can't save you from a misidentified treatment. Hours after Elon Musk closed his acquisition of Twitter, he tweeted "the bird is freed." Molak [used this event](https://medium.com/data-science/causal-python-elon-musks-tweet-our-googling-habits-bayesian-synthetic-control-187114fc4aa8) to demonstrate how synthetic control can estimate causal effects from observational data. Synthetic control constructs a counterfactual by weighting a set of comparison time series (in this case, Google search trends for LinkedIn, TikTok, and Instagram) to match the pre-treatment trajectory of the treated unit. Any post-treatment divergence between the actual and synthetic series is attributed to the treatment. Using this approach, Molak found a large effect of Musk's tweet on Google searches for "Twitter."

![Google search interest for "Twitter" was already surging days before the tweet, driven by acquisition news coverage](/img/posts/causal-inference/freebird-trends.svg)

This was a clean application of a cutting-edge method. The comparison set was reasonable. The pre-treatment fit was good. The model produced a crisp estimate with a clear divergence at the treatment date. But as the author correctly notes, the outcome "might be influenced not only by Musk's tweet but also by other factors (e.g. media publications on Twitter acquisition)." The acquisition dominated the news cycle for days before the tweet went out. People were already searching for "Twitter" because of the takeover itself, not because of one tweet. Musk's acquisition of Twitter and the tweet weren't independent events.

There is no diagnostic that would have caught this. Placebo tests, in-space or in-time, would pass. The pre-treatment fit is fine because the problem isn't in the pre-treatment period. The search trends used to construct the counterfactual are reasonable for normal search behavior. The threat is upstream of every check the method provides. Synthetic control answers the question "what would searches for Twitter have looked like without this event?" The problem is that "this event" isn't one tweet, it's a major news item that generated weeks of media coverage. The model can't distinguish the tweet from the acquisition because they're the same story.

The method answered the question it was given just fine. The question just wasn't the right one. Nothing in the output would say that. The only way to catch this is by knowing the timeline, following the news cycle, thinking about what else was happening when the "treatment" occurred. That's not a statistical skill. It's the kind of contextual judgment that no framework can formalize and no robustness check can replace.

## Still Easy, Still Hard

Causal inference is easy to understand. Eliminate alternative explanations. The frameworks, whether DAGs or potential outcomes, formalize this task. But doing it well requires knowing what the alternatives are, measuring the variables behind them, and designing comparisons that make specific threats implausible when measurement falls short.

The Mozart study was a controlled experiment with random assignment. The synthetic control analysis of Musk's tweet used a cutting-edge method with a reasonable comparison set and strong pre-treatment fit. Both produced clear, defensible-looking results. Both got the wrong answer, and for essentially the same reason: the treatment contrast didn't isolate what the researchers thought it did. Mozart wasn't compared to "no music." It was compared to boredom. Musk's tweet wasn't an isolated event. It was one moment in a weeks-long news cycle. In neither case did the output raise a flag.

That's the core difficulty. The model will always estimate the treatment effect you ask for and produce a clean-looking result. Nothing in the output distinguishes a valid causal estimate from one that's been quietly undermined. The math works. The question is whether it's working on the right problem.

[^1]: Rauscher, Shaw & Ky (1993). Music and spatial task performance. *Nature*, 365, 611.

[^2]: Nantais & Schellenberg (1999). The Mozart effect: An artifact of preference. *Psychological Science*, 10(4), 370-373; Thompson, Schellenberg & Husain (2001). Arousal, mood, and the Mozart effect. *Psychological Science*, 12(3), 248-251.

