---
title:       "Causal Inference Is Hard"
subtitle:    "Part two of a two-part series"
description: "How I learned to stop worrying and love assumptions"
date:        2026-03-15
author:      "MJ"
image:       ""
tags:        ["causal inference"]
categories:  []
draft:       FALSE
---


The [first post](/post/causal-inference-is-easy/) argued that causal inference is just a matter of ruling out rival explanations. That sounds straightforward. But rival explanations can be hard to identify, hard to measure, and hard to isolate. Overlook a confound, measure it poorly, or choose an inadequate study design, and causal inference fails. No matter how sophisticated the method, the model will estimate the treatment effect you ask for and produce a number. When causal inference fails, it fails silently.

### Rock Me Amadeus

In 1993, researchers had college students listen to Mozart, a relaxation tape, and silence for 10 minutes then take a spatial reasoning test. Participants scored highest after listening to Mozart.[^1] Despite the study being designed to test the effects of music on cognition, headlines announced that Mozart makes you smarter. Mozart for babies CDs appeared and some states passed legislation encouraging music in schools.

The conditions in the original study didn't just differ in the presence of Mozart. They also differed in arousal and mood. Follow-up studies found that other enjoyable stimuli (e.g., Schubert, a Stephen King story) produced similar boosts, and that the effect disappeared when researchers controlled for arousal and mood.[^2] The active ingredient seemed to be a stimulating experience, not Mozart.

The confound here wasn't statistical, it was conceptual. Comparing Mozart to silence or relaxation instructions doesn't isolate Mozart. It confounds music with the psychological experience of music. Engagement, pleasure, stimulation. The confound was baked into the treatment contrast. The researchers wanted to test the effect of music on spatial reasoning, but the comparison tested whether an engaging experience outperformed a boring one.

### Knowing What to Worry About

The Mozart study was a tightly controlled experiment and a confound still slipped through. In observational studies, where you have little control, the threats only multiply. Identifying them requires knowing the subject matter well enough to see what else could be driving the result.

The relationship between smartphones and teen mental health is a case in point. Starting around 2012, rates of anxiety, depression, and self-harm among adolescents increased across multiple surveys. Smartphone adoption also increased around this time. The timing lines up and the causal story practically writes itself. But "seems obvious" is where observational research goes to die.
There were various other events around that time, many of which could generate similar patterns.

The Great Recession's aftermath left families under sustained economic stress into the 2010s. Academic pressure intensified as college admissions grew more competitive. School shootings became a recurring feature of adolescent life. These are history effects, events external to the treatment that coincide with it and could independently produce the observed outcome. These are the kind of threats that require domain expertise to identify. They don't show up in the dataset.

Then there are the changes in how the outcome itself is measured. In 2009, the U.S. Preventive Services Task Force recommended routine depression screening for adolescents. The following year, the Affordable Care Act required insurers to cover it, making screening far more common. More screening mechanically produces more diagnoses, even if the underlying rate hasn't changed. Coding changes in how hospitals recorded suicidal ideation had a similar effect.[^3] Add the destigmatization of mental health making teens more willing to report symptoms, and you have an outcome variable that can shift for reasons entirely unrelated to smartphone use.

This is not to say that smartphones are harmless. It means observational evidence can't cleanly separate the smartphone signal from the noise of everything else that changed. Ruling out one rival explanation leaves a half-dozen others. Even if you identified every one, they still need to be measured well enough to neutralize any confounding influence.

### Measuring the Weight of Smoke

The smartphone debate illustrates the challenges of identifying confounders. But even when you know what the confounders are, measuring them is not always straightforward.

In the HRT example, we specified health consciousness as the main confound. How do you measure that? The Nurses' Health Study tried. Researchers collected data on diet, exercise, smoking status, alcohol use, preventive care visits, and vitamin supplementation. They controlled for all of it. The treated and untreated groups still weren't comparable, because health consciousness isn't just a checklist of behaviors. It's the disposition behind those behaviors, the kind of person who asks her doctor about hormone therapy in the first place. The observational studies captured the visible markers of health consciousness but missed the underlying trait that drove both HRT use and cardiovascular health. Controlling for the markers didn't eliminate the confounding. It just left residual bias in the estimate.

Many variables that matter for causal inference are abstract constructs. Motivation, risk tolerance, management quality, organizational culture. We give them names and put them on a scale, but translating them into numbers that capture what actually drives selection is a different challenge entirely.

Causal inference frameworks require that you've measured all the confounders, not just some of them. If health consciousness has three dimensions and you only capture two, the unmeasured dimension still confounds your result. The carefully matched samples are not comparable in the ways that matter.

If we can’t measure the confounds well enough, we need another strategy.

### Design Around What You Can't Measure

Design offers one approach to valid causal claims when confounders are hard to quantify. Instead of making assumptions, you select a design so that plausible confounds can't explain the pattern of results. The threats are ruled out by principled comparisons.

Difference-in-differences illustrates this logic. Instead of comparing HRT users to non-users at a single point in time, we compare changes over time. If health-conscious women are consistently more likely to use HRT, the baseline difference captures that. By looking at whether the trend in cardiovascular outcomes shifted after HRT adoption, you neutralize any baseline difference between groups that remains stable over time, including unmeasured ones. The design handles what measurement can't.

{{< figure src="/img/posts/causal-inference/did-hrt.svg" caption="Stylized illustration of a difference-in-differences design. Data are simulated for explanatory purposes and do not represent actual HRT study results." class="img-center" >}}

Design-based approaches trade one assumption for another. Instead of assuming we measured everything, we assume that treated and untreated groups would have followed the same trend without the treatment. That's less demanding, but it can still fail silently. The parallel trends assumption is untestable in the post-treatment period. An event that coincides with treatment and differentially affects the groups will bias the estimate, and nothing in the data will tell you it happened. The design shifts the burden from measurement to plausibility but it doesn't eliminate it.

### Free Bird

Even sophisticated methods can't avoid a misidentified treatment. Hours after Elon Musk closed his acquisition of Twitter, he tweeted "the bird is freed." Molak [used this event](https://medium.com/data-science/causal-python-elon-musks-tweet-our-googling-habits-bayesian-synthetic-control-187114fc4aa8) to demonstrate how synthetic control can estimate causal effects from observational data. Synthetic control constructs a counterfactual by weighting a set of comparison time series (in this case, Google search trends for LinkedIn, TikTok, and Instagram) to match the pre-treatment trajectory of the treated unit. Any post-treatment divergence between the actual and synthetic series is attributed to the treatment. Using this approach, Molak found a large effect of Musk's tweet on Google searches for "Twitter."

![Google search interest for "Twitter" was already surging days before the tweet, driven by acquisition news coverage](/img/posts/causal-inference/freebird-trends.svg)

This was a clean application of a contemporary method. The controls were reasonable. The model produced a robust estimate with a clear divergence at the treatment date. But as the author correctly notes, the outcome "might be influenced not only by Musk's tweet but also by other factors (e.g. media publications on Twitter acquisition)." The acquisition dominated the news cycle for days before the tweet. People were already searching for "Twitter" because of the takeover itself, not because of one tweet. Musk's acquisition of Twitter and the tweet weren't independent.

No diagnostic test would have caught this. The pre-treatment fit looks good. The uncertainty intervals are tight. Every quantitative check gives a green light because the problem isn't in the pre-treatment period. The threat is upstream. Synthetic control answers the question "what would searches for Twitter have looked like without this event?" The problem is that "this event" isn't one tweet, it's major news that generated weeks of coverage. The model can't distinguish the tweet from the acquisition because they're the same story.

The method answered the question it was given just fine. The data just weren't suited to that question. Nothing in the output would say that. The only way to catch this is by knowing the timeline, following the news, considering what else was happening when the "treatment" occurred. That's not a statistical skill. It's situational awareness that no framework can formalize and no robustness check can replace.

## Still Easy, Still Hard

The Mozart study was a randomized experiment. The synthetic control analysis used a powerful contemporary method. Both produced clear, defensible results. Both got the wrong answer, for the same reason: the treatment contrast didn't isolate what the researchers thought it did. Experiments don't solve the problem automatically. Neither do sophisticated statistical methods. The hard part is always upstream of the technique.

The model will always estimate the treatment effect you ask for. Nothing in the output distinguishes a valid causal estimate from one that's been quietly undermined. The math works. The question is whether it's working on the right problem.

[^1]: Rauscher, Shaw & Ky (1993). Music and spatial task performance. *Nature*, 365, 611.

[^2]: Nantais & Schellenberg (1999). The Mozart effect: An artifact of preference. *Psychological Science*, 10(4), 370-373; Thompson, Schellenberg & Husain (2001). Arousal, mood, and the Mozart effect. *Psychological Science*, 12(3), 248-251.

[^3]: Corredor-Waldron & Currie (2024). To what extent are trends in teen mental health driven by changes in reporting? The example of suicide-related hospital visits. *Journal of Human Resources*, 59(S), S14-S40.
