---
name: "high-standard-agent-playbook"
description: "Guides high-standard Agent planning, benchmark filtering, boundary control, and stabilization. Invoke when starting a new Agent project, comparing competitors, or closing architecture debt."
---

# High Standard Agent Playbook

Use this skill when the task is not just "build something", but "build it in a way that stays stable, scoped, and maintainable".

## When to Use

Invoke this skill when any of the following is true:

- You are starting a new Agent project or a new major phase.
- The user asks for PRD, alignment, design, task split, acceptance, or final summary documents.
- The team wants to compare benchmark or competitor Agents before implementation.
- The current project is drifting, accumulating architecture debt, or losing a single main path.
- You need to stabilize a late-stage project and prevent more structural debt.

## Core Position

This skill is a workflow guardrail, not a substitute for product direction.

It should help you:

- define the product promise before expanding code
- freeze one main path before adding parallel solutions
- filter competitor inspiration before importing ideas
- treat documentation as a cost-control tool
- prove no-regression before claiming structure improvement

## Mandatory Principles

1. Write a minimum PRD before broad implementation.
2. Freeze the single main path early.
3. Separate default capability, experimental capability, and future capability.
4. Prefer small reversible refactors over multi-axis rewrites.
5. Do not mix routing, auth, runtime core, and UI behavior changes in one pass.
6. Do not let benchmark code create a second architecture beside the first one.
7. Do not allow stabilization phase to become another exploration phase.

## Workflow

### Phase A: Minimum PRD

Before major implementation, define:

- target users
- top 3 recurring tasks
- default promise
- explicit non-goals
- downgrade strategy on failure
- measurable acceptance standard

If these are not clear, pause broad coding work.

### Phase B: Main Path Freeze

Confirm and write down:

- single entry
- single UI path
- single task submission flow
- single state query path
- single error envelope
- single default runtime promise

Do not add major features until these are stable.

### Phase C: Competitor Filtering

For each benchmark idea, answer:

1. What exact problem does it solve?
2. Do we really have that problem?
3. Is this missing from our current main path?
4. Can it fit into the current boundary?
5. Will it create a second parallel architecture?

If question 4 or 5 is unclear, do not directly implement it.

### Phase D: Controlled Execution

Use the following order:

1. interface boundary
2. service logic
3. caller wiring
4. tests and verification

Each round should cut one coherent slice only.

### Phase E: Stabilization

Late-stage work should focus on:

- narrowing active entry points
- closing documentation drift
- reducing startup and import-time side effects
- tightening verification evidence
- documenting rollback points

Do not keep mixing in new frameworks, new entry paths, or fresh competitor patterns at this stage.

## Required Documents

For serious Agent work, prefer maintaining:

- `ALIGNMENT_*`
- `CONSENSUS_*`
- `DESIGN_*`
- `TASK_*`
- `ACCEPTANCE_*`
- `FINAL_*`
- `TODO_*`

These documents are part of delivery quality, not optional paperwork.

## Verification Standard

Before claiming stability or structure improvement, confirm:

- the default promise is documented
- the main path is still singular
- contracts and error envelopes are consistent
- logs are readable enough for diagnosis
- focused verification exists
- rollback points are known
- current docs point to the active truth

## Anti-Patterns

- Long-term implementation without a minimum PRD
- Importing multiple same-level benchmark solutions at once
- Treating "it ran once" as a default promise
- Mixing entry refactor, runtime core, auth, and UI changes together
- Letting docs trail behind the real system
- Continuing exploration after the project should already be stabilizing

## Expected Output

When using this skill, leave behind:

- a clear project promise
- a narrowed scope
- explicit non-goals
- a documented main path
- a small-step execution plan
- verification evidence or a concrete verification checklist

## Repository Note

In this repository, also cross-check:

- `AGENTS.md`
- `auto_agent/docs/HIGH_STANDARD_AGENT_PLAYBOOK.md`
- existing project-specific alignment, consensus, design, and final docs
