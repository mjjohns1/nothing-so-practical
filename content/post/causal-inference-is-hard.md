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


The [first post](/post/causal-inference-is-easy/) argued that causal inference is just a matter of ruling out rival explanations. That sounds straightforward. But rival explanations can be hard to identify, hard to measure, and hard to design around. Overlook a confound, measure it poorly, or choose an inadequate study design, and causal inference fails, no matter how sophisticated the method. The model will estimate the treatment effect you ask for and produce a number. When causal inference fails, it fails silently.

### Rock Me Amadeus

In 1993, researchers had college students listen to Mozart, a relaxation tape, or silence for 10 minutes then take a spatial reasoning test. Participants scored highest after listening to Mozart.[^1] Despite the study being designed to test the effects of music on cognition, headlines announced that Mozart makes you smarter. Mozart for babies CDs appeared and some states passed legislation encouraging music in schools.

The conditions in the original study didn't just differ in the presence of Mozart. They also differed in arousal and mood. Follow-up studies found that other enjoyable stimuli (e.g., Schubert, a Stephen King story) produced similar boosts, and that the effect disappeared when researchers controlled for arousal and mood.[^2] The active ingredient seemed to be a stimulating experience, not Mozart.

The confound here wasn't statistical, it was conceptual. Comparing Mozart to silence or relaxation instructions doesn't isolate Mozart. It confounds music with the psychological experience of music. Engagement, pleasure, stimulation. The confound was baked into the treatment contrast. The researchers wanted to test the effect of music on spatial reasoning, but the comparison tested whether an engaging experience outperformed a boring one.

### Knowing What to Worry About

The Mozart study was a tightly controlled experiment and a confound still slipped through. In observational studies, where you have little control, the threats only multiply.

Consider the questions about smartphones and teen mental health. Starting around 2012, rates of anxiety, depression, and self-harm among adolescents increased across multiple surveys. Smartphone adoption also increased over the same period. The timing lines up. The mechanism seems plausible. The causal story practically tells itself. But "seems obvious" is where observational research goes to die.
There were lots of other changes during that time, many of which could generate the same pattern.

The Great Recession's aftermath left families under sustained economic stress into the 2010s. Academic pressure intensified as college admissions grew more competitive. School shootings became a recurring feature of adolescent life. These are history effects, events external to the treatment that coincide with it and could independently produce the observed outcome. A developmental psychologist or social worker would flag economic insecurity and academic pressure. A data scientist might not.

Then there are the changes in how the outcome itself is measured. In 2009, the U.S. Preventive Services Task Force recommended routine depression screening for adolescents. The following year, the Affordable Care Act required insurers to cover it, making screening far more common. More screening mechanically produces more diagnoses, even if the underlying rate hasn't changed. Coding changes in how hospitals recorded suicidal ideation had a similar effect.[^3] Add the destigmatization of mental health making teens more willing to report symptoms, and you have an outcome variable that can shift for reasons entirely unrelated to smartphones.

This is not to say that smartphones are harmless. It means observational evidence can't cleanly separate the smartphone signal from the noise of everything else that changed. Ruling out one rival explanation leaves a half-dozen others. And even if you identified every one of them, you'd still have to measure each well enough to neutralize its confounding influence.

### Measuring the Weight of Smoke

The smartphone debate illustrates the problem of identifying confounders. But even when you know what the confounders are, measuring them is its own challenge.

What is "health consciousness", for example? You could ask people to rate how important their health is. But how many people would endorse the idea that they don't care about their health? Maybe you build a composite index combining multiple indicators. But which onrs? How do you weight them? Each choice makes assumptions about the construct. If your measure doesn't capture what matters for both HRT use and heart disease, controlling for it doesn't eliminate the confounding. It just leaves residual bias in your estimate.

Many variables that matter for causal inference are abstract constructs, like motivation, risk tolerance, management quality, organizational culture. We give them names and put them on a scale, but translating them into numbers that can capture what actually drives selection is a different challenge entirely.

Causal inference frameworks require that you've measured all the confounders, not just some of them. If health consciousness has three dimensions and you only capture two, the unmeasured dimension still confounds your result. The carefully matched samples are not comparable in the ways that matter.

This is the bind. The variables that matter most can be the hardest to measure. If we can't measure them well, we need another strategy.

### Design Around What You Can't Measure

Design offers one approach to valid causal claims when confounders are hard to quantify. Instead making assumptions, you select a design so that plausible confounds can't explain the pattern of results. The threats are ruled out by principled comparisons.

Difference-in-differences illustrates the logic. Instead of comparing HRT users to non-users at a single point in time, we compare changes over time. If health-conscious women are consistently more likely to use HRT, the baseline difference captures that. By looking at whether the trend in cardiovascular outcomes shifted after HRT adoption, you neutralize any baseline difference between groups that remains stable over time. Even unmeasured ones. The design handles what measurement can't.

{{< figure src="/img/posts/causal-inference/did-hrt.svg" caption="Stylized illustration of a difference-in-differences design. Data are simulated for explanatory purposes and do not represent actual HRT study results." class="img-center" >}}

This trades one assumption for another. Instead of assuming we measured everything we assume that treated and untreated groups would have followed the same trend without the treatment. That's less demanding, and it's the kind of claim where domain expertise becomes relevant. But it can still be wrong in ways that are hard to detect. The parallel trends assumption is untestable in the post-treatment period. An event that coincides with treatment and differentially affects the groups will bias the estimate. The design shifts the burden from measurement to plausibility but it doesn't eliminate it.

### Free Bird

Even sophisticated methods can't avoid a misidentified treatment. Hours after Elon Musk closed his acquisition of Twitter, he tweeted "the bird is freed." Molak [used this event](https://medium.com/data-science/causal-python-elon-musks-tweet-our-googling-habits-bayesian-synthetic-control-187114fc4aa8) to demonstrate how synthetic control can estimate causal effects from observational data. Synthetic control constructs a counterfactual by weighting a set of comparison time series (in this case, Google search trends for LinkedIn, TikTok, and Instagram) to match the pre-treatment trajectory of the treated unit. Any post-treatment divergence between the actual and synthetic series is attributed to the treatment. Using this approach, Molak found a large effect of Musk's tweet on Google searches for "Twitter."

![Google search interest for "Twitter" was already surging days before the tweet, driven by acquisition news coverage](/img/posts/causal-inference/freebird-trends.svg)

This was a clean application of a contemporary method. The controls were reasonable. The model produced a robust estimate with a clear divergence at the treatment date. But as the author correctly notes, the outcome "might be influenced not only by Musk's tweet but also by other factors (e.g. media publications on Twitter acquisition)." The acquisition dominated the news cycle for days before the tweet went out. People were already searching for "Twitter" because of the takeover itself, not because of one tweet. Musk's acquisition of Twitter and the tweet weren't independent.

No diagnostic test would have caught this. The pre-treatment fit is fine because the problem isn't in the pre-treatment period.  The threat is upstream. Synthetic control answers the question "what would searches for Twitter have looked like without this event?" The problem is that "this event" isn't one tweet, it's major news that generated weeks of coverage. The model can't distinguish the tweet from the acquisition because they're the same story.

The method answered the question it was given just fine. The data just weren't suited to that question. Nothing in the output would say that. The only way to catch this is by knowing the timeline, following the news, considering what else was happening when the "treatment" occurred. That's not a statistical skill. It's situational awareness that no framework can formalize and no robustness check can replace.

## Still Easy, Still Hard

Causal inference is easy to understand. Just eliminate alternative explanations. The frameworks, whether DAGs or potential outcomes, formalize this task. But doing it well requires identifying the threats, measuring the variables behind them, and designing comparisons that make specific alternatives implausible when measurement falls short.

The Mozart study was a controlled experiment. The synthetic control analysis used a powerful statistical method. Both produced clear results. Both got the wrong answer, for essentially the same reason: the treatment contrast didn't isolate what the researchers thought it did.

The model will always estimate the treatment effect you ask for. Nothing in the output distinguishes a valid causal estimate from one that's been quietly undermined. The math will work. The question is whether it's working on the right problem.

[^1]: Rauscher, Shaw & Ky (1993). Music and spatial task performance. *Nature*, 365, 611.

[^2]: Nantais & Schellenberg (1999). The Mozart effect: An artifact of preference. *Psychological Science*, 10(4), 370-373; Thompson, Schellenberg & Husain (2001). Arousal, mood, and the Mozart effect. *Psychological Science*, 12(3), 248-251.

[^3]: Corredor-Waldron & Currie (2024). To what extent are trends in teen mental health driven by changes in reporting? The example of suicide-related hospital visits. *Journal of Human Resources*, 59(S), S14-S40.

