---
title:       "Abelson's Laws"
subtitle:    "Chance is lumpy"
description: "Statistics as Principled Argument is over 30 years old. Abelson's laws are timeless."
date:        2026-03-02
author:      "MJ"
image:       "img/posts/abelson/stats-as-principled-arg.jpg"
tags:        ['statistics', 'psychology']
categories:  []
draft:       FALSE
---

## Abelson's Laws

[Robert Abelson](https://en.wikipedia.org/wiki/Robert_Abelson) was a faculty member in the Yale Psychology Department for almost 5 decades. He did trailblazing research that helped lay the foundation for the cognitive revolution in psychology and was early to adopt computer programming to model social cognitive processes. He also worked with John Tukey on his "Swing-o-metric" technique for predicting election results, becoming one of the early political psychologists.[^1]

Among contemporary researchers, he is probably best known for his work in statistics and methods. I discovered Abelson in graduate school when digging into the literature on statistical interactions. A faculty member subsequently introduced me to his 1995 book, [*Statistics as Principled Argument*](https://books.google.com/books/about/Statistics_as_Principled_Argument.html?id=TgmbosIA7N0C).

{{< figure src="/img/posts/abelson/stats-as-principled-arg.jpg" alt="Statistics as Principled Argument" width="30%" class="img-center" >}}

It instantly became my favorite book about statistics, mainly because it's not really a stats book. It also doesn't hurt that it's a quick and entertaining read, at least for a book about analyzing data.

The book is based on 35 years of experience teaching statistics to first-year grad students. Abelson's approach is practical, emphasizing conceptual understanding over technical minutiae. He drills to the core of how statistics are used out in the world: quantifying evidence and supporting arguments. The results of any analysis are not some truth but merely proof points used to support a claim. Data can't speak for themselves. A convincing finding is as much about narrative and rhetoric as it is about the specific technique used to compute the results. This is applied causal inference in a nutshell.

The book contains a lot of useful heuristics, like the ["MAGIC"](https://en.wikipedia.org/wiki/MAGIC_criteria) criteria, and plenty of campy humor. That unruly data point? It isn't an outlier, it's a Klinker\! But for me the most useful and memorable insights are the laws, delivered right up front before Chapter 1:

##### Abelson's Laws

1. Chance is lumpy.
2. Overconfidence abhors uncertainty.
3. Never flout a convention just once.
4. Don't talk Greek if you don't know the English translation.
5. If you have nothing to say, don't say anything.
6. There is no free hunch.
7. You can't see the dust if you don't move the couch.
8. Criticism is the mother of methodology.


I've invoked the first Law on many occasions when discussing the pitfalls of small samples and the confusion that follows a weird or surprising result. Lumpiness is easy to overlook. I'm also fond of Law 4, which captures a problem I've observed too often in how quantitative methods are communicated. Equations are not a replacement for understanding. If you can't explain your model in plain language, you probably don't understand it.

But it is the 2nd Law, "Overconfidence abhors uncertainty," that has always stuck with me. I didn't appreciate this point when I first read it. Over the years, trying to find terra firma in a sea of random processes, I've come to realize that unshakeable *certainty* is one of the best ways to end up being wrong.

Abelson understood this. The title of his book frames statistics as *argument*, not *proof*. An argument can be convincing but it is never the final word. Data are evidence in support of a claim, not the final verdict. When we treat a statistically significant result as settled fact, we conjure up a world free of measurement error, filled with perfect models and infinite samples.

The replication crisis drove this point home. When the Open Science Collaboration tried to replicate 100 published psychology studies, only about 36% produced significant results in the original direction. Daniel Kahneman captured the overconfidence that pervaded the pre-crisis era in *Thinking, Fast and Slow* (2011) when explaining why we MUST believe the results of studies that are hard to believe:

> The idea you should focus on, however, is that disbelief is not an option. The results are not made up, nor are they statistical flukes. You have no choice but to accept that the major conclusions of these studies are true. More important, you must accept that they are true about you.

Yes, that Daniel Kahneman. He supposedly came to regret this statement once the full scope of the problem became clear, calling the replication failures a trainwreck and a mess. But it illustrates what can happen when a field treats statistical results as certainties. The most we can hope to achieve with a piece of quantitative work (i.e. analysis, model, experiment) is reducing our uncertainty.

Many of Abelson's laws can be seen as warnings against the pitfalls of overconfidence. Law 1 is a reminder that randomness can look like a signal. Law 2 warns that you'll want to believe the signal anyway. Law 6 tells you that chasing patterns after the fact can be costly. Law 7 says you have to actively look for what's wrong. Together, they create a checklist for keeping yourself honest.

##### References

Abelson, R. P. (1995). *Statistics as Principled Argument*. Lawrence Erlbaum Associates.

Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

Open Science Collaboration (2015). Estimating the reproducibility of psychological science. *Science*, 349(6251), aac4716.

[^1]: He also managed to get his own [paradox](https://en.wikipedia.org/wiki/Abelson%27s_paradox). When analyzing the batting performance of major league players, he found that for any single at bat, skill explained only a tiny fraction of the variance. The paradox is that skill doesn't seem to explain the differences between players despite the fact that we know it matters.