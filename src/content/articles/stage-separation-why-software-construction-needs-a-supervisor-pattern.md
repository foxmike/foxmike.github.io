---
title: "Stage Separation: Why Software Construction Needs a Supervisor Pattern"
slug: "stage-separation-why-software-construction-needs-a-supervisor-pattern"
order: 3
source_docx: "abracapocus_articles/3. Stage Separation: Why Software Construction Needs a Supervisor Pattern.docx"
description: "Most AI development tools share a default shape: one model acting as planner, builder, reviewer, verifier, and project memory, all inside a single conversational loop."
---
Most AI development tools share a default shape: one model acting as planner, builder, reviewer, verifier, and project memory, all inside a single conversational loop.

This is not a design choice. It is what you get when an LLM is wrapped in chat and pointed at a task. It works for exploration, where the work is short and wrong turns are cheap. It fails for software construction, where the work is long, state must survive interruptions, and the agent that produced the work cannot also be the authority that accepts it.

Dependable software construction needs stage separation as a property of the system itself: planning, execution, review, and verification as distinct stages with explicit handoffs, not as behaviors one agent performs inside one loop. The pattern that organizes these stages is the supervisor pattern.

The choice between a single-loop system and a supervisor pattern is the foundational architectural decision in any AI development system meant to do construction work reliably.

Beneath that choice is a simpler distinction. Exploration discovers what the work should be. Construction preserves and completes work that already has a definition. They are different problems, and they reward different system shapes.

### Why the single-loop pattern is the default

The default is not a design decision. It follows from how LLMs are easiest to use.

Wrap a model in a chat interface. Give it tool access. Ask it to do a task. Now you have a system. Nothing has been engineered. No architecture has been imposed.

The model plans in the same response in which it executes. It judges its own work in the next sentence. State lives in the chat history, which means it dies when the chat ends.

For exploration, this is fine. Planning, doing, and judging are provisional, and the next session can start fresh because little has accumulated that needs preserving.

For construction, the same shape is corrosive. The damage stays hidden until the work has gone on long enough for state to matter.

### What construction actually requires

Construction has requirements that exploration does not.

Work must be repeatable: the same task should produce the same shape of output across runs. Scope must stay bounded to what was asked for, not expand silently when the model notices an adjacent problem. Acceptance criteria must exist before the work starts, not be discovered after.

Multiple bounded tasks must also compose into something coherent without losing architectural direction across the seams. State must survive interruption. Work done over three days will cross sessions, machines, and restarts. And someone must be able to tell, after the fact, what was decided, what was rejected, what was verified, and why the work was accepted.

None of these are natural strengths of a single-loop system.

A loop that mixes planning, execution, and judgment has no durable place for any of them. The plan is whatever the model said early in the response. Acceptance is whatever it said at the end. State is chat history. The audit trail is chat history.

When the chat ends, most of what mattered ends with it.

This is not a defect of any particular model. It is what happens when one structural element is asked to do every job.

### What stage separation changes

Stage separation breaks the loop into pieces with defined responsibilities and defined outputs:

Planning outputs intent. Execution outputs a diff. Review outputs judgment. Verification outputs evidence.

State and progress are managed outside any individual stage, in a place that survives any single component restarting. The supervisor owns the state transitions; the stages perform the work.

The point is not bureaucracy. The point is detection.

A planner that also executes is biased toward plans it can execute easily. An executor that also reviews is biased toward reviewing favorably. A verifier that shares the executor's context inherits the executor's assumptions about what the task meant.

Splitting the roles does not make any one role smarter. It makes the system's failures detectable, because each stage produces an output the next stage can examine.

Review and verification deserve separate stages because they answer different questions.

Review asks whether the work is directionally and architecturally right—the kind of judgment a senior engineer brings to a pull request. Verification asks whether objective acceptance checks pass: tests, contracts, builds, schema validation.

Review can catch scope expansion that passes the tests. Verification can catch contract failures that pass review. A system that runs both has two different surfaces on which wrong-but-plausible work can be caught.

Separation also creates the surfaces a dependable system needs. Policy lives somewhere explicit: scope rules, architectural constraints, backend and model rules, retry policy, commit policy, and verification requirements. It is not buried in prompt text. Retry logic has a home. Checkpoints fire on defined triggers. State outlives any single conversation because it never lived in the conversation in the first place.

In code, the supervisor assembles stages with explicit outputs and handoffs, and attaches state outside any stage:

graph = StageGraph()

graph.add_stage("planning", produces="intent")

graph.add_stage("execution", produces="diff")

graph.add_stage("review", produces="judgment")

graph.add_stage("verification", produces="evidence")

graph.connect("planning" -\> "execution")

graph.connect("execution" -\> "review")

graph.connect("review" -\> "verification")

graph.connect("verification" -\> "commit_or_reject")

\# State lives outside the stages, not inside the conversation.

graph.attach_state_store(DurableCheckpointStore(path="state/checkpoints"))

Four named stages, four distinct outputs, four explicit handoffs, and a state store attached to the graph rather than carried inside any stage.

### Resumability and durable state

Construction work is resumable in a way exploration is not.

A feature that takes three days to build will be interrupted. The machine will restart. The session will close. The work must survive these interruptions in a way conversation does not.

In a single-loop system, resumption means starting fresh and re-establishing context: what was being done, what was decided, what was tried. Some of the most expensive failures in AI-assisted development happen in this gap between sessions, where context is rebuilt imperfectly and decisions are quietly relitigated.

Stage separation moves state out of the conversation and into something durable. The next session reads the state. It does not have to remember it.

This is also where verification gets its operational home. Article 1 argued that verification is the load-bearing element of dependable AI-assisted development. Stage separation makes verification more than a prompt instruction.

The verifier is a stage. It runs after execution. It produces evidence. Its judgment is not folded into the executor's narration—which, as Article 2 argued, cannot close the loop anyway.

The mechanism is small. After each stage runs, the supervisor records the result in storage that survives a process restart, and on resume the next session reads state instead of reconstructing it:

def on_stage_complete(stage, result, run_id):

state = state_store.read(run_id)

state.last_stage = stage.name

state.last_output = result.output \# intent \| diff \| judgment \| evidence

state.last_status = result.status \# passed \| failed \| rejected

state.history.append(result) \# including rejected attempts and reasons

state_store.write(run_id, state)

def resume(run_id):

state = state_store.read(run_id)

return graph.continue_from(state.last_stage, state)

Every stage outcome — including rejections and the reasons for them — is durable. Resumption is a read, not a reconstruction.

### A construction loop in practice

A concrete shape makes the pattern clearer.

In a working supervisor system, a task begins as a contract: a JSON document defining intent, scope, constraints, and acceptance criteria. The contract is written before the work starts and is not modified by the agents executing it.

A coding backend receives the task and produces changes on an isolated branch. Branch-per-task isolation keeps the blast radius bounded and makes rejection cheap. The reviewer assesses the change against the contract. The verifier runs the acceptance checks. Only if both pass does the supervisor commit the work.

State persists outside any conversation, including rejected attempts and the reasons they were rejected.

Picture one failure case. An agent implements a task, modifies the tests to match the behavior it produced, and reports success.

In a single-loop system, that may complete the work: the agent's report is the only acceptance signal.

In a supervisor system, it does not. Either the verifier runs against contract tests the executor cannot edit, or the reviewer notices that the test changes are doing different work than the contract called for, or both. The work does not commit. The branch is discarded. The supervisor records why.

### How to recognize a single-loop system

The diagnostic is straightforward once you know where to look:

Where does the plan live? In a single-loop system, in the chat. In a supervisor system, in a contract that exists before execution.

Where does acceptance live? In a single-loop system, in the agent's report. In a supervisor system, in a verifier that runs separately.

Where does state live? In a single-loop system, in the conversation history. In a supervisor system, in durable storage owned by the supervisor.

What happens after interruption? In a single-loop system, the next session has to reconstruct what mattered. In a supervisor system, the next session reads it.

The loop works for exploration because exploration seeks shape. It fails for construction because construction must produce something that holds.

### Won't stronger models make this unnecessary?

The likely objection is that stronger models will absorb the supervisor's work: better planning inside the loop, better self-review, fewer false completions.

Stronger models do reduce per-task error. They do not remove the need for durable state, acceptance authority outside the agent that produced the work, or an audit trail that survives the conversation. Those are needs of construction work, not weaknesses of current models.

A stronger model in a single-loop system is still an agent in a system with nowhere durable to put the work that matters across sessions.

A supervisor pattern is not a smarter agent. It is a system that prevents any one agent from owning intent, execution, acceptance, and memory at once.

The supervisor does not make agents infallible. It makes their fallibility governable.

### Closing

The choice between a single-loop system and a supervisor pattern is foundational for any system meant to do construction work.

It is not chiefly about agent sophistication, model power, or clever prompts. It is about whether the system has the structural surfaces construction depends on: state, policy, verification, and resumption.

A careful operator can impose discipline on a single-loop system. Many do. But once discipline must survive turnover, fatigue, restart, and pressure to ship, habits are not enough.

At that point, discipline must become part of the system.

The supervisor pattern is that architecture. Stage separation is what it is made of.
