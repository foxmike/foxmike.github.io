---
title: "Anti-Patterns in AI-Assisted Development"
slug: "anti-patterns-in-ai-assisted-development"
order: 9
source_docx: "abracapocus_articles/9. Anti-Patterns in AI-Assisted Development.docx"
description: "A methodology needs diagnostic instincts, not just recommended patterns."
---
A methodology needs diagnostic instincts, not just recommended patterns.

The positive patterns in dependable AI-assisted development are clear: verification as acceptance gate, task contracts as work units, staged supervision, multi-backend routing, tiered retry, bounded blast radius, and curated execution. Those describe what to build toward.

This article describes the inverse: what fragile workflows look like. The goal is to help practitioners inspect their own systems and distinguish structural soundness from operator intuition holding everything together.

None of these anti-patterns is rare. Most are the default. They emerge when AI-assisted development begins as a convenience and never becomes an architecture. The workflow accumulates habits instead of structures. The habits work until the work becomes repeated, consequential, or unsupervised.

## Chat as system of record

The first and most common anti-pattern is using conversation history as the system of record.

The chat window is where the work was discussed, so it becomes where the work lives. The goal sits somewhere in the first few messages. The constraints appear halfway through. The acceptance standard is implied by the operator’s reaction to an earlier attempt. The current state is whatever the last response contained.

That is fragile in every dimension that matters. Context windows truncate. Sessions expire. The operator switches devices, takes a break, or hands the work to someone else. The state of the work vanishes with the conversation.

The operator becomes the backup system, carrying project state in memory. Without that operator, the work cannot resume. No one else can inspect it. The history is an unstructured transcript, not an operational record.

The corrective is durable state: structured run reports, task status, checkpoint records, and execution artifacts that survive beyond any single conversation.

## No durable work contract

Intent is implied, not explicit.

The operator describes what they want. The agent interprets. The interpretation may be correct, or it may be only plausible. There is no artifact both sides can inspect to verify alignment before execution begins.

“Fix the dashboard” is not the same as a task with target files, acceptance criteria, and verification commands. The first is a wish. The second is a contract.

Without a durable work contract, scope is negotiated in real time. The agent acts on its interpretation. The operator reacts to the result. Corrections accumulate during execution, when they are most expensive, rather than during specification, when they are cheapest.

## No clear acceptance boundary

Completion becomes self-reported or socially inferred.

The agent says it is done. The operator glances at the output. It looks reasonable. The work is accepted — not because it passed a deterministic check, but because it appeared plausible and the operator was ready to move on.

This is open-loop execution. Without an external acceptance boundary, the system’s own confidence becomes the evidence for completion. A fluent explanation, a long diff, and a detailed summary may feel like completion signals. They are not acceptance signals.

The corrective is a verification gate that decides acceptance independently of the agent’s self-report. The form varies: test suite, compile check, contract validation, schema check, targeted script. The principle does not. Completion is decided outside the model.

## Planning, execution, and judgment collapsed together

When one agent plans the work, executes the work, and judges the result, failure signals blur.

If the plan is wrong, the agent may not know; it is executing its own plan. If the execution drifts, the agent may not know; it is judging its own drift. If the result misses the operator’s intent, the agent may not know; it is evaluating against its own interpretation of that intent.

This is the unreliable narrator problem expressed as architecture. The agent becomes the sole authority on what was intended, what was attempted, and whether the result is acceptable. Every assessment passes through the same interpretive lens, and that lens cannot reliably detect its own distortion.

Stage separation creates the surfaces where failure becomes visible. Separate planning, execution, review, and verification roles give the system places to catch its own mistakes.

## Retries without failure classification

The system wanders.

A task fails. The system retries. It fails again. The system retries again. Each attempt may fail for a different reason, but the system does not distinguish between them. A syntax error and an intent mismatch receive the same treatment: another attempt with the same or similar prompt.

Without failure classification, retry is hope rather than policy. The system cannot decide whether to try the same approach with corrected details, escalate to a stronger backend, or stop for human guidance. It cannot tell whether attempts are converging or drifting apart.

The corrective is a failure classifier and a retry policy. Mechanical failures get enriched retry. Capability shortfalls get escalation. Specification failures get checkpointed and blocked.

## Broad autonomy with large blast radius

The agent can do too much, too widely.

It can write across the repository. It can modify any file, install packages, change configuration, and push to any branch. Its autonomy is unconstrained not because anyone decided it should be, but because no one constrained it.

When the agent is right, this is invisible. When it is wrong, the damage is expensive: files modified across unrelated modules, changes tangled into the main branch, no clean rollback path.

Containment does not make the agent smarter. It makes being wrong cheaper. Working-root boundaries limit the write surface. Branch-per-run isolation keeps bad changes off protected branches. Auto-commits create restore points. Structured reports make wrong actions visible.

## Single-vendor dependence mistaken for simplicity

The workflow uses one model provider because it is convenient. Convenience hardens into dependence. Prompts acquire workarounds for that model’s habits. Parsers depend on its output format. The team’s productivity becomes tied to one provider’s product decisions.

Then the provider raises prices, changes rate limits, deprecates a version, or ships a regression. The team experiences someone else’s roadmap as an outage in its own work.

The corrective is multi-backend routing: an orchestrator that treats backends as replaceable workers behind a stable interface. Backend choice becomes policy, not identity.

## Plausible output treated as success

This differs from having no acceptance boundary, though the two often appear together. A missing acceptance boundary means there is no external gate. This anti-pattern means the gate exists in theory, but fluency substitutes for evidence when applying it.

The agent produces output that reads well, explains itself clearly, and appears to address the task. The operator accepts it because it is plausible: detailed, fluent, internally consistent.

Plausibility is not correctness. A model can explain a change beautifully and still break the build. It can summarize work that drifted from the original intent. It can report success with complete confidence while a verification check would reject the result.

The corrective is verification that judges the work, not the explanation. Tests check behavior, not summaries. Compile checks verify structure, not narrative. Contract validation checks criteria, not confidence.

## Prompt polish mistaken for architecture

When the system produces bad output, the first instinct is to improve the prompt.

Better prompts help. They reduce ambiguity, provide examples, and constrain output format. They are useful.

But prompts do not replace state, contracts, gates, routing, retry, or containment. A better prompt in an open-loop system produces better output on average, but still has no mechanism to detect or recover when the output is wrong.

The danger is that prompt improvement feels like architectural improvement. Each revision makes the system a little better. The workflow feels as if it is maturing. But the maturity is in the input signal, not in the control structure. The system is becoming better at asking. It is not becoming better at verifying, retrying, containing, routing, or recovering.

The diagnostic is simple: if the prompt were perfect, would the system still need an acceptance gate?

Yes. Models are stochastic, context is incomplete, and requirements change. If the system needs a gate even with a perfect prompt, prompt polish cannot substitute for building the gate.

## Human babysitting mistaken for dependable orchestration

The machine appears autonomous because the operator silently compensates.

The agent runs. It produces output. The operator reviews, corrects, reruns, adjusts, and redirects. The agent runs again. The operator reviews again. After several cycles, the result is acceptable. The system gets credit for the output.

The operator’s contribution disappears in this accounting. Planning happened in the operator’s head. Quality control happened in the operator’s judgment. Error correction happened in the operator’s edits between runs. The agent executed, but the orchestration was human.

The diagnostic is whether the system could produce an accepted result if the operator walked away after submitting the task. If the answer is no, the system is not autonomous. The operator is.

## The contrasting patterns

Each anti-pattern has a structural corrective, and the correctives reinforce one another.

Durable state replaces chat as system of record. Task contracts replace implied intent. Verification gates replace self-reported completion. These three answer the foundation questions: where the work lives, what it means, and how acceptance is decided.

Stage separation replaces the collapsed loop, creating failure surfaces the system can inspect. Failure classification and tiered retry replace blind repetition, giving the system policy rather than hope when things go wrong. Containment replaces unconstrained autonomy, bounding the cost of each wrong action.

Multi-backend routing replaces single-vendor dependence. Curated task execution replaces false autonomy. Structural investment replaces the illusion that better prompts alone will close the reliability gap.

None of these correctives is exotic. Each is a straightforward architectural decision. The difficulty is not building any one of them. The difficulty is recognizing that the anti-patterns are problems, because the anti-patterns feel normal. They are the default.

## Closing

The goal of this diagnostic is not to shame lightweight workflows.

Many of these anti-patterns are acceptable for casual use: one-off tasks, exploration, prototypes, or work where the cost of being wrong is low and the operator is present. A developer using a chat-based agent to sketch an idea does not need durable state, task contracts, and multi-backend routing. The workflow is fine because the stakes are low and the human is the system.

The anti-patterns become problems when the work becomes repeated, consequential, or unsupervised. When the system is expected to run overnight. When the output becomes committed code. When the cost of being wrong is measured in hours of cleanup rather than minutes of re-prompting.

At that threshold, the question changes from “does this work?” to “is this dependable?” Dependability requires structural answers, not better habits.

The diagnostic question for any AI development workflow is this: is the system structurally sound, or is it held together by operator intuition?

If removing the operator from the loop would make the workflow collapse, the system does not have the architecture required for the autonomy it has been granted.
