---
title: "Curated Task Execution Beats Dynamic Planning in Real Work"
slug: "curated-task-execution-beats-dynamic-planning-in-real-work"
order: 8
source_docx: "abracapocus_articles/8. Curated Task Execution Beats Dynamic Planning in Real Work.docx"
description: "The dream is seductive: give the system a goal and let it figure out the rest."
---
The dream is seductive: give the system a goal and let it figure out the rest.

Describe what you want in a sentence or two. The agent plans the work, breaks it into steps, executes each step, and delivers the result. No manual task shaping. No hand-written acceptance criteria. No operator in the loop until final approval.

This vision dominates the conversation around AI-assisted development. It appeals because it sounds like the logical endpoint: advanced, autonomous, intelligent, scalable.

In most real construction work today, it disappoints.

The argument is not against planning agents. Planning is useful. The argument is against treating unvalidated autonomous planning as execution authority — letting a planning agent’s output bypass the contractual standards that govern every other unit of work.

The distinction matters. Planning can generate candidate tasks. Execution must run acceptance-bound tasks. These are different activities with different requirements. When the two are conflated — when the plan becomes an executable contract without review, shaping, or validation — the result is predictable.

## Why dynamic planning appeals

Dynamic planning appeals because it resembles intelligence.

An agent that plans its own work looks smarter than one that executes pre-written tasks. It looks more autonomous, more general, more capable. It suggests that the system understands the problem deeply enough to decompose it without human help.

Demos intensify the appeal. A small, self-contained problem with clear boundaries makes dynamic planning look effortless. The agent reasons about the goal, proposes a plan, executes it, and produces working code. The audience then extrapolates from the demo to production-scale construction.

That extrapolation is where the trouble begins.

## Why it often disappoints in real construction

The main gap between demo and production is a specification gap.

In a demo, the goal is chosen for clarity. The boundaries are obvious. The acceptance standard is simple: does the code run?

In real construction, the goal is often ambiguous, the boundaries are contested, and “does the code run?” is the lowest bar, not the standard of acceptance.

When a dynamically planning agent meets ambiguity, it rarely stops to demand precision. It guesses. It fills gaps with plausible assumptions. It produces work that may be locally correct but aligned to an invented version of the goal.

The pattern is familiar.

Hidden operator correction: the agent plans and executes, but the operator repeatedly redirects, clarifies, or repairs. The system appears autonomous. In practice, the operator is doing the planning work during execution, reacting to the agent’s guesses rather than shaping the work in advance. The planning labor has not disappeared. It has been scattered.

Broad ambiguity at execution time: because the plan was generated from a vague goal, the tasks inherit that vagueness. Each task carries the ambiguity forward instead of resolving it. The verification layer, if one exists, must accept or reject work against criteria that were never made explicit.

Weak acceptance: when the plan is dynamic, the same system often generates both the work and the standard for judging it. The agent writes its own test. It decides what “done” means while deciding what to do. Acceptance cannot safely be authored by the same process being judged unless an external gate holds the standard independently.

Wandering execution: without sharp task boundaries, the agent drifts. “Add error handling” becomes “refactor the error module,” which becomes “update the logging configuration.” Each step may be locally reasonable. Together they become scope drift no one authorized.

Retrospective cleanup: the operator receives the final result and compares it with the original intent. The gap is often large enough that cleanup costs as much as specification would have cost in the first place.

## Why curated tasks perform better

A curated task has its boundaries, acceptance criteria, and constraints shaped before execution begins.

That shaping is the work.

It is not overhead. It is not bureaucracy. It is the act that gives execution a fair chance of producing accepted output.

Curated tasks perform better because they resolve ambiguity before the agent acts.

A task with explicit acceptance criteria gives verification something to check. “The function handles the three error types listed in the criteria” is verifiable. “Add error handling” is not.

A task with a scoped description narrows the agent’s write surface. The agent knows which files are in play and which are not. Wandering becomes harder because the task contract defines relevance.

A task with a selected backend and verification profile lets the system apply the right worker and the right checks. Routing is part of execution intent. It belongs in the contract, not in runtime improvisation.

A task that fails produces a clear signal. The failure is measured against known criteria. Retry logic can classify the failure, enrich the next attempt, and decide whether escalation is warranted because the contract defines success. Without that definition, failure is vague and retry is guesswork.

The economic argument follows. Curated tasks reduce the cost of wrong execution by narrowing the space of wrong outputs. They reduce verification cost by making acceptance explicit. They reduce failure cost by making retry rational. Each saving is small per task and large across dozens or hundreds of tasks.

## Where dynamic planning still belongs

Dynamic planning is not useless. It is miscast.

It is valuable for ideation: generating candidate approaches, surfacing options the operator had not considered, and exploring the solution space before the team commits.

It is valuable for decomposition support: taking a large goal and proposing a breakdown the operator can review, refine, and approve before execution. The planning agent’s output is a draft, not an execution plan.

It is valuable for research: gathering context, reading documentation, summarizing codebases, and answering questions about what already exists before the operator decides what to build.

In each role, dynamic planning supports judgment rather than replacing it. The agent contributes intelligence. The operator contributes intent. The task contract is where those contributions meet.

Future planning agents may become strong enough to sit at the center of dependable execution. The present does not justify that trust. Today, the reliable path is to use dynamic planning as input to curated execution, not as its substitute.

## The evidence from practice

The strongest evidence for curated task execution is operational.

In abracapocus_2, the enhancement plan was executed this way. A system that built itself across eight phases and thirty-seven tasks used curated task contracts as its unit of work. Each task carried explicit acceptance criteria, a scoped description, a selected backend, and a verification profile. The methodology was both the subject and the evidence.

A representative task contract looks like this:

```json
{
  "task_id": "3.2",
  "title": "Rewrite PlanningAgent.create_plan() with complexity awareness",
  "description": "Import and call ComplexityClassifier before generating phases...",
  "phase": "phase_3",
  "acceptance_criteria": [
    "Single-criterion task produces single-phase plan",
    "Five-criterion task produces five or more tasks across phases",
    "Each task has selected_backend set",
    "Plans persist correctly to plans/ directory"
  ],
  "selected_backend": "codex_cli",
  "verification_profile": "strict"
}
```

Every field does work. The task_id anchors the task in the plan. The acceptance criteria define what the verification gate will check. The selected backend is a routing decision, not a default. The verification profile determines how strictly the result will be judged.

Contrast that with the dynamic alternative: “Rewrite the planning agent to use complexity scoring.”

That sentence contains intent, but not a contract. It does not specify what a correct result looks like. It does not tell verification what to check. It does not tell retry logic what failure means. It is a goal, not a work unit.

The contract also enables pre-execution validation. Before any backend runs, the system can check whether the contract is sound:

```python
if not task.acceptance_criteria:
    return ContractValidationResult(
        status="failed",
        reason_codes=["missing_acceptance_criteria"],
        detail="Acceptance criteria must be non-empty.",
        blocking=True,
    )
```

A task with empty acceptance criteria is blocked before it reaches a backend. A task with tautological criteria — “task is complete,” “works,” “done” — is flagged. A task whose criteria reference file paths not mentioned in the description is flagged for surface contradiction.

That is why curated tasks are more than better prompts. They are objects the system can reject before execution.

This is the frame layer discussed earlier in the series: the structure that constrains the agent before execution, complementing the verification gate that judges it after. Dynamic planning often does not produce contracts clean enough to survive this check, because the planning agent optimizes for plausibility rather than contractual precision.

## What false autonomy looks like

False autonomy has recognizable symptoms.

The system looks autonomous but depends on operator cleanup. The agent runs, produces output, and waits while the operator corrects what missed, reruns what failed, and adjusts what drifted. The system’s contribution is real, but the autonomy is theater. The operator is doing planning and quality control in real time instead of in advance.

Tasks remain vague until late. The system defers specification until execution, so the agent meets ambiguity during the run rather than before it. Each ambiguity becomes a guess. Each guess becomes a possible misalignment discovered only at review.

Success is judged after the fact. There are no predefined acceptance criteria. The operator looks at the result and decides whether it is close enough. “Close enough” is not a verification standard. It is a negotiation between expectation and fatigue.

“It got close” becomes the real success standard. That may be acceptable for a research assistant. It is not acceptable for a construction system whose output becomes committed code.

The diagnostic question is whether the system could run the same task unattended and produce an accepted result. If success assumes an attentive operator, the autonomy is not in the system. It is in the operator.

## The objection and its limits

The objection is that curated task execution sounds less advanced. It requires human effort to shape the work. It does not match the dream of fully autonomous AI development. It feels like a concession.

It is less theatrical, not less effective.

A curated task that runs, passes verification, and produces accepted code is more advanced in any operational sense than a dynamically planned task that produces impressive output requiring an hour of cleanup.

Dependable construction is a higher standard than impressive demos. A demo optimizes for audience reaction. A construction system optimizes for accepted output at rational cost. Those objectives favor different architectures.

The near-term advantage belongs to systems that specify work well, not because specification is the final answer, but because it is the current bottleneck. Models can often execute well-specified tasks reliably in real codebases. They cannot yet reliably specify their own work to the standard dependable construction requires.

When that changes, the architecture should change with it. Until then, curated execution is not a compromise. It is the stronger operating model.

## Closing

Dependability currently comes from shaping work well, not from maximizing agent freedom.

The most reliable systems are not the ones with the most autonomy. They are the ones with the sharpest tasks: explicit acceptance criteria, bounded scope, deliberate backend choice, and a verification layer with something concrete to check.

Dynamic planning will improve. Models will get better at decomposition, edge cases, and contract writing. When that happens, the right response is to let planning agents produce curated tasks that meet the same contractual standard — not to abandon the standard.

The diagnostic question for any AI development workflow is this: is the system executing against well-shaped contracts, or interpreting vague goals and hoping the operator will clean up the difference?

If autonomy depends on cleanup, it is not autonomy. It is delegation with hidden labor.
