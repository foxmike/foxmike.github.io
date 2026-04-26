---
title: "Task Contracts as the Unit of Work in AI-Assisted Development"
slug: "task-contracts-as-the-unit-of-work-in-ai-assisted-development"
order: 4
source_docx: "abracapocus_articles/4. Task Contracts as the Unit of Work in AI-Assisted Development.docx"
description: "The prompt is the most familiar artifact in AI-assisted development. It is what users type, tools log, tutorials teach, and operators often mistake for the work itself."
---
The prompt is the most familiar artifact in AI-assisted development. It is what users type, tools log, tutorials teach, and operators often mistake for the work itself.

But the prompt is not the unit of work. It is only an input signal: what gets handed to a model so the model can begin. It is not a durable record of what the work is supposed to be, what counts as done, or what the executor must not do.

Dependable AI-assisted development needs a durable work contract: a structured task artifact that defines intent, scope, acceptance criteria, and execution constraints in a form the system can enforce. The usual shape is JSON. JSON is not magic. Structure is doing the work.

A dependable AI development system cannot treat the prompt as memory, policy, scope, and acceptance criteria at once. Those are different jobs. They need different homes.

For exploration, the distinction matters little. The prompt is the input. The conversation is the work. The work ends when the session does.

For construction, the distinction matters greatly. The work must outlive the conversation. It must be resumable, auditable, and enforceable against criteria defined before execution. A prompt cannot do those jobs. Prose invites interpretation in exactly the places construction needs limits.

The diagnostic question is simple: **where does the intent of the work actually live?**

If the answer is “in the prompt,” “in the chat,” or “in what I told the model last,” the system has no contract. It has a conversation, and the conversation is being asked to do work it was not built to do.

## Why prompts break down under repeated work

A prompt that produces good output once has proved only that one run worked. It has not defined the work.

Run the same prompt again with a different model version, a different context window, or a different set of files, and it may produce a different result. The prompt did not change. The system around it did.

Without a contract independent of the prompt, there is no stable way to say which result was correct.

The failures compound under repetition. Repeated work exposes weakness in four areas: repeatability, drift, resumption, and auditability.

Ambiguity that is tolerable in one session becomes drift across many sessions. Each new run inherits a slightly different reading of the same idea. Constraints that were assumed but never stated get violated later. Acceptance criteria that lived in the operator’s head get re-derived each session, slightly differently each time.

Resumption is worse. Picking up work after a break, or on another machine, means re-explaining what was being built and hoping the new explanation matches the old one.

Auditability is where the failure becomes plain. When work is defined by a prompt, the question “why was this accepted?” has no strong answer. The agent reported success. The operator reviewed the output. Approval happened in a chat that may or may not still exist.

A contract-based system can point to something durable: a task ID, acceptance criteria, verification results, a commit hash, the backend and model that produced the change. Six weeks later, that record is still there. The transcript may not be.

Article 2 argued that agents cannot be trusted to notice when guessed intent has replaced understood intent. The contract is where intent is made explicit before that substitution begins.

Prompts are good at starting work. They are bad at being work.

## What an executable contract is

A task contract is a structured document, written before execution, that defines the work in terms the system can act on.

It is not a tidier prompt. It is a different artifact with a different job.

The prompt is a communication artifact: what an operator types to direct attention.  
The task contract is a system artifact: what the supervisor and its stages read and act on.  
The verification profile is an acceptance mechanism: the rules by which a result is judged.  
The supervisor is the orchestration mechanism: the component that moves a contract through the stages.

These are separate concerns. Conflating them produces single-loop systems that make the prompt carry all four jobs.

“Executable contract” does not mean the JSON itself runs code. It means the system can use the artifact directly: route on its fields, verify against its criteria, retry on its terms, and resume from its state. The system does not read it as background prose and improvise the rest.

Structure is what separates a contract from a prompt. A prose request invites the agent to interpret: fill gaps, infer intent, decide what was meant. Structured fields reduce that freedom. A field for acceptance criteria either contains acceptance criteria or it does not. A field for scope either constrains the work or it does not.

The agent still interprets, but now it interprets inside a bounded contract rather than an open request.

## What the JSON carries

A real contract from a working supervisor system looks like this:

{

"task_id": "1.3",

"title": "Add item detail retrieval",

"description": "Implement item-detail retrieval for selected listing IDs from the candidate set so downstream phases can normalize richer listing payloads.",

"phase": "phase_1",

"acceptance_criteria": \[

"Item-detail retrieval accepts one or more item IDs from search output.",

"Detail responses are mapped into a stable raw artifact structure with source metadata.",

"Missing or invalid listing IDs are handled without crashing the acquisition run."

\],

"selected_backend": "codex_cli",

"verification_profile": "default",

"model": "codex"

}

Each field does specific work. Two carry most of the weight.

The description field carries purpose. It does not merely say what to build; it says why the change exists. That lets downstream stages and later readers judge whether later decisions match the original intent. A description that says only what to build leaves the why in the operator’s head, which is only another version of putting intent in the chat.

The acceptance_criteria field is the most important field in the document. It defines what the verifier will check. The executor cannot skip it by reporting success on adjacent grounds.

This is where Article 1’s argument becomes operational: verification is the load-bearing element of dependable AI-assisted development, and acceptance criteria are what the verifier verifies against. Without them, the verifier has nothing specific to enforce. It falls back on generic checks that may or may not catch the right failure.

The remaining fields define identity and routing. task_id and phase give the work a stable name that persists in storage, audit trails, and later reports. selected_backend, verification_profile, and model define routing and execution policy explicitly, so they survive across runs and do not depend on operator memory.

Notice what is missing: there is no prompt in the colloquial sense. The agent does not receive an open request to interpret. It receives a contract to satisfy.

## How the supervisor uses it

Once the work has durable structure, every part of the system can act on it.

Planning produces contracts, not prompts. Execution satisfies a contract. Routing follows fields the contract carries: backend, model, verification profile. Review and verification assess against something explicit. Retry knows what failed. Resumption knows what was being attempted.

The operational pattern is small:

for task in task_contracts:

result = supervisor.run(task) \# planning, execution, review, verification

if result.accepted:

commit(result)

record(task, result)

else:

record(task, result) \# including the reasons for rejection

continue \# or escalate, depending on policy

The shape of the loop is the shape of the argument.

The contract is the unit being passed in. The supervisor’s stages run against it. The commit happens only if the result is accepted. The record is written either way, so rejected attempts and their reasons survive audit.

The contract is what lets the supervisor be more than a wrapper around a prompt. Without contracts, this loop is only a sequence of free-form requests, each requiring an operator at the handoff. With contracts, the loop can run across many tasks because the system has something concrete to operate on at each step.

This also makes verification operational. Article 1 argued that verification is the load-bearing element of dependable AI-assisted development. Article 3 argued that verification needs its own stage in the supervisor pattern. Neither works without a contract.

A verifier with no contract has nothing to verify against. The best it can do is run generic checks and hope they catch the right wrong. With a contract, the verifier knows what passing means.

The contract does not remove judgment from the system. It prevents judgment from being hidden inside a single model response. Judgment moves to the right places: before execution, in the contract; after execution, in review and verification.

## Why this is not bureaucracy

The objection comes quickly: this is too heavy for normal development. Writing JSON for every task sounds like ceremony. The time spent producing contracts feels like overhead.

But the comparison is wrong. The alternative to writing a contract is not writing nothing. It is writing a prompt, then writing follow-up prompts as the agent drifts from intent. It is reviewing output that solves a nearby problem. It is steering the agent back toward the actual problem. It is reconstructing context next session because the previous chat is gone. It is explaining six weeks later why a change was made, using a transcript that may no longer exist.

Contracts are heavier than prompts. They are lighter than the cleanup prompts require when the work is non-trivial.

The break-even point often arrives sooner than expected: once the same task survives more than one interaction. Past that point, the contract is the cheaper artifact.

Bureaucracy is process that produces no useful information. A contract produces information: what was intended, what counts as done, and what was constrained.

That information is the substrate every other reliability mechanism needs.

## Where intent lives: the diagnostic

The diagnostic question remains: **where does the intent of the work actually live?**

In a prompt-based workflow, intent lives in the chat. Scope lives wherever the agent happened not to drift. Acceptance lives in the agent’s report. State lives in the conversation history. The audit trail lives in whatever transcript still exists.

In a contract-based workflow, intent lives in the task document. Scope lives in the contract’s constraints. Acceptance lives in the verifier’s assessment against the acceptance criteria. State lives in durable storage owned by the supervisor. The audit trail lives in recorded results keyed to task IDs that persist across runs.

Both systems can produce good work. Only one can reliably produce it.

In the prompt-based version, reliability depends on the operator catching divergence in real time. The operator becomes the contract: holding intent in memory, comparing output against it, correcting drift as it appears.

That works at small scale. It does not survive turnover, fatigue, or time.

## Closing

The unit of work in dependable AI-assisted development is not the prompt. It is the contract.

Prompts will continue to exist. They are how operators communicate with the system, and they remain the natural medium for exploration.

But once the work matters, once it must outlive its session, once it must be enforceable against criteria, something else must carry it.

A structured task document carries it.

Without that document, the supervisor pattern from Article 3 has nothing to enforce. Verifiers verify against guesses. Reviewers review against intuition. The system’s reliability machinery compensates for a missing foundation.

The question to keep is simple: **where does the intent of the work actually live?**

If the answer is “in the conversation,” there is no contract. If the answer is “in a document the system reads and acts on,” there is.

That document is the unit of work.
