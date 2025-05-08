---
layout: docs
title: Rule Experiments
permalink: docs/rule-experiment/
---


## Experiments

Experiments are similar to A/B Testing. The use case is, if you have a new version of a rule, or a different rule that you want to try out with real traffic, you can create an experiment that consists of both versions or both rules, and see how the two versions or the two different rules perform by splitting traffic.

For example, you have defined the following versions of the same rule:

Version #1:
```scala
if (x > 90) "BLOCK" else "PASS"
```

Version #2:
```scala
if (x > 80) "BLOCK" else "PASS"
```

### How to create an experiment

1. In order to participate in an experiment, a rule (or a version) must be in the status of Live. Make sure you have set the status of such rule or such version to Live, otherwise it will not appear in `Create Rule Experiment` wizard (explained next).

![de](/img/experiment1.png)

2. Go to `Profiles` page, and select a profile you want to add experiments to. Click the `More Options` button and then `Create Rule Experiment` at the bottom of the pop-up menu. This will open the `Create Rule Experiment` modal dialog.

3. In this dialog, enter a name and a description. Then in step 1, select a rule as the Profile Rule in your experiment and click the `Next Step` button. 

![de](/img/experiment2.png)

4. In step 2, select a rule/version as your Test Rule and continue by clicking the `Next Step` button.

![de](/img/experiment3.png)

5. In step 3 (the last step), specify how the traffic should be split percentage-wise for these two rules/versions. Then click the `Create Experiment` button to save your experiment.

![de](/img/experiment4.png)

Once you apply this new experiment to Rule Engine by clicking the `Deploy Rules` button in the main Profiles page, your experiment will be live and traffic will be split according to the percentages. Experiment results are fully audited on which rule is evaluated. This means you can create reports showing how requests are processed according to the traffic split.
