---
title: "Tiered Retry Is a Failure Economy"
slug: "tiered-retry-is-a-failure-economy"
order: 6
source_docx: "abracapocus_articles/6. Tiered Retry Is a Failure Economy.docx"
description: "These systems fail often enough that failure handling cannot be a secondary concern. It is a primary execution path."
---
These systems fail often enough that failure handling cannot be a secondary concern. It is a primary execution path.

An AI coding agent working against a real codebase will meet syntax errors, test failures, missing dependencies, ambiguous requirements, and plain misunderstandings of intent. These failures are varied, frequent, and structurally inevitable. They must be handled somewhere.

The question is not whether failure will occur. It is whether the system treats failure as architecture or as an afterthought.

Most systems treat it as an afterthought. The agent fails. The operator notices. The operator retries, perhaps with a tweaked prompt, a different model, or a sigh and a manual fix. The system itself has no judgment about what happened or what should happen next.

A dependable system treats failure handling as a control loop: execution, verification, classification, adjusted attempt, escalation decision. That loop is bounded, classified, and able to stop when further effort is no longer rational.

If verification is the acceptance gate, retry governs what happens when that gate rejects the work.

## Why naive retry is wasteful

The simplest retry strategy is repetition: the task failed, so run it again.

But a retry that introduces no new information is not a retry. It is repetition.

Blind repetition wastes time, because each attempt has real duration. It wastes money, because API calls and compute scale with attempts. It produces little signal, because the system does not know why it failed and cannot guide the next attempt. And it creates false momentum: activity looks like progress while the agent wanders across files and interpretations, expanding the blast radius without increasing confidence.

Naive retry is uncontrolled expenditure attached to the hope that randomness will converge.

## Failure types matter

The first requirement for rational failure handling is classification. Not all failures are alike.

A syntax error is mechanical. The agent produced invalid code. Retrying with the error message in context has a high chance of success.

A test failure may indicate a misunderstanding of expected behavior. A missing-file error suggests a false assumption about project structure. An import error reveals a dependency gap.

These are retryable failures: failures where new information gives the next attempt a structural reason to behave differently.

Other failures are not autonomously retryable. The verification gate rejects the work, but the rejection points to ambiguous requirements. The agent completed something, but not the right thing. The specification never made clear what “correct” meant.

These are not retry problems. They are intent problems or specification problems. No amount of repeated execution will fix a task whose acceptance criteria are ambiguous or whose necessary context was never provided.

The architectural consequence is simple: failure classification must precede retry. A syntax error needs a different response from an intent mismatch. An environmental failure needs a different response from a logic error. Even a coarse taxonomy — syntax, import, test, missing file, logic, unknown — gives retry logic something to reason about. Blind repetition gives it nothing.

## Bounded escalation

Once failures are classified, the system can apply a tiered response.

The first tier is same-backend retry with enriched context. The failure classification, stderr output, affected files, and prior diff are fed back to the same backend, along with an explicit instruction not to repeat the same approach. This is the cheapest response and handles most mechanical failures.

The enrichment is what separates this from repetition. The retry prompt carries the previous failure detail, the files that changed, and a suggested focus area. The agent now has information the first attempt lacked. It has a reason to behave differently.

The second tier is escalation to a stronger or more specialized backend. If the same-model retry fails, the system routes the task to a model with a larger context window or stronger reasoning capability. This costs more per attempt, but applies more capability to a problem that has already resisted the cheaper option.

Escalation is not a search for a model more likely to pass without meeting the contract. The task contract and acceptance criteria do not change. The verification gate does not relax. The system is asking a more capable worker to meet the same standard.

The third tier is checkpoint and block. The system stops autonomous execution, records the full attempt history, and marks the task as blocked.

In abracapocus_2, retry tiers are represented as an explicit finite budget:

```python
def _retry_tiers(self) -> List[int]:
    tier_1 = int(getattr(retry_config, "max_retries_tier_1", 2))
    tier_2 = int(getattr(retry_config, "max_retries_tier_2", 1))
    tier_3 = int(getattr(retry_config, "max_retries_tier_3", 1))
    return [1] * tier_1 + [2] * tier_2 + [3] * tier_3
```

Two same-model retries. One stronger-model escalation. One final attempt before blocking.

The numbers can be tuned by project, risk tolerance, and cost sensitivity. The principle does not change: bounded expenditure, then stop.

## Why checkpoints are a strength

Stopping is part of dependable behavior.

Most AI development workflows encourage the opposite instinct: keep trying. The model is available. The quota has room. The task is not done. Why stop?

Because effort without convergence is waste. Each failed attempt that changes the code in a new way expands the work the operator must later understand. Each failed attempt that repeats the same pattern confirms that the approach is wrong, not that the budget was too small.

A system that blocks a task and writes a structured report is making a rational economic decision: autonomous effort has reached diminishing returns. The next productive step requires human judgment — to clarify the specification, provide missing context, or admit that the task was ill-defined.

The blocked-task report preserves full diagnostic context:

```json
{
  "task_id": "phase5-retry-loop",
  "run_id": "a1b2c3d4",
  "reason": "convergence_wandering",
  "attempts": [
    {
      "attempt_number": 2,
      "tier": 1,
      "failure_type": "test",
      "failure_detail": "test_retry_escalation: AssertionError",
      "convergence_assessment": {"status": "converging"}
    },
    {
      "attempt_number": 3,
      "tier": 2,
      "failure_type": "logic",
      "failure_detail": "Repeated unclassified failure across retry attempts",
      "convergence_assessment": {
        "status": "wandering",
        "reasons": ["divergent_regions"]
      }
    }
  ]
}
```

The operator who receives this report does not need to reconstruct the failure from scratch. The system has preserved what was tried, what failed, how the failure was classified, and why it stopped.

Checkpointing is not weakness. It is the system recognizing the boundary of its own useful effort.

## Convergence detection

Most systems have retry. Few can detect when retry has stopped being productive.

Bounded retry is necessary, but not sufficient. A system can exhaust its retry budget methodically and still waste most of that budget on attempts that were never converging. Convergence detection short-circuits the retry loop when evidence shows the system is wandering rather than approaching a solution.

Three signals suggest wandering.

The set of changed files grows across attempts: the agent is expanding its search rather than narrowing it.

The diff regions become disjoint across attempts: the agent is trying unrelated approaches in different parts of the codebase.

The verifier failure pattern changes across attempts: the agent is not fixing the original problem but creating new ones.

Any of these signals can trigger early termination:

```python
convergence = self.convergence_detector.assess(attempts)

if convergence.status == "wandering":
    task.status = "blocked"
    self._persist_blocked_report(reason="convergence_wandering")
    return
```

The distinction between convergence_wandering and retry_budget_exhausted matters. Budget exhaustion means the system tried and ran out of room. Wandering means continued effort was unlikely to help, regardless of budget.

That small amount of code has a large economic effect. It converts retry from fixed-budget expenditure into an adaptive loop that stops when the cost-to-signal ratio has collapsed.

## What bad retry looks like

Bad retry has recognizable symptoms.

The system retries without classifying the failure. Every attempt gets the same prompt. The retry has no structural advantage over the original attempt: no new information, no adjusted focus, no reason to expect a different result.

The system has no convergence awareness. Cost grows while confidence does not. The operator sees activity and mistakes it for progress.

The system does not distinguish capability shortfall from specification failure. A syntax error and an ambiguous requirement receive the same treatment: another attempt.

The system has no stopping condition except the operator’s patience or a rate limit.

The diagnostic signal is cost growth without confidence growth. If the system spends more per cycle but the failures are not becoming more specific, more local, or more fixable, the retry strategy is not working. It is merely running.

## The objection and its limits

The common objection is that a stronger model can often push through. Why classify and tier retries when immediate escalation to the best available model might solve the problem faster?

Sometimes it would. But stronger models are expensive, and expense is not the only issue. A stronger model cannot compensate for ambiguous intent. If the task specification is unclear about what “correct” means, a more capable model may produce only a more elaborate wrong answer.

Escalation as the first response also destroys the information that tiered retry produces. When the cheaper model succeeds, the system learns that the task class is within its capability. When the cheaper model fails and the stronger model succeeds, the system learns something about the boundary between them. When both fail, the system learns that the problem is likely specification, not capability.

That learning is lost if every task goes directly to the strongest model. The system becomes more expensive without becoming more informed.

The rational position is not to avoid stronger models. It is to use them as escalation targets, not defaults: cheap attempts first; expensive attempts when cheaper attempts fail in ways that suggest capability shortfall rather than specification failure.

## Closing

Dependable automation is not about avoiding failure. It is about handling failure with bounded logic and rational cost.

A system that classifies failures, enriches retry prompts with diagnostic context, escalates through capability tiers, detects wandering, and stops when continued autonomous effort is irrational treats failure as architecture. It has an economic policy for failure, not merely a habit.

The alternative is a system that retries because it can, stops because the operator noticed, and converts bad luck into unbounded cost.

The diagnostic question for any AI development workflow is this: when a task fails, does the system know what kind of failure it is, what to try next, and when to stop?

If the answer to any of those is no, the system is spending money on hope.
