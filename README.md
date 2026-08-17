# IDE Data Science Club — Project Template

A starter repository for **project managers (PMs)** in the IDE Data Science Club. Fork or "Use this template" to spin up a new project with the conventions, workflow, and scaffolding the club expects already in place.

## What's in here

| File / folder | Purpose |
|---|---|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **Start here.** How the team runs the project on GitHub — PM vs. member roles, the issue → PR → `main` flow, branching, worktrees, and reviews. |
| [`DELIVERABLES.md`](DELIVERABLES.md) | The PMs' estimated deliverables and a rough timeline. A living plan, not a contract. |
| [`DATA.md`](DATA.md) | Where the project's data comes from, how to find sources, and how to think about using them. Tracked in git. |
| [`data/`](data/) | Working folder for actual datasets. **Git-ignored** — data never gets committed. |
| [`AGENTS.md`](AGENTS.md) | The strict, machine-facing version of the workflow, for AI coding agents. |

## How to use this template

1. **Create your repo from it.** On GitHub, click **Use this template → Create a new repository** (or fork it), then clone your copy.
2. **Read [`CONTRIBUTING.md`](CONTRIBUTING.md).** Everyone on the team reads it; it's the operating manual.
3. **Fill in [`DELIVERABLES.md`](DELIVERABLES.md)** with your project's real deliverables and dates.
4. **Fill in [`DATA.md`](DATA.md)** with your actual data sources.
5. **Turn on branch protection** for `main` (require a PR + one approval) and, ideally, **enable a code-review agent** (Codex or Claude auto-review) — see CONTRIBUTING.
6. **Open your first issue** and run the flow.

## The one-paragraph version

Every change starts as a GitHub **Issue**, gets built on a **branch** (organized as a small tree per issue, each slice optionally in its own **worktree**), is opened as a **pull request**, reviewed (by a teammate and, ideally, an auto-review agent), and merged **up the tree**. Only a **PM** merges the issue's integration branch into `main`. `main` is always in a known-good state. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full workflow.
