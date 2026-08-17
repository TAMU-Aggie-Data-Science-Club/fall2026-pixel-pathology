# Deliverables & Timeline

> **How to read this file.** This is the PMs' best current estimate of what the project needs to ship and roughly when. It is a **living plan, not a contract** — deliverables will be added, dropped, split, or resequenced as the team learns more. The authoritative, up-to-the-minute picture always lives in the repo's **GitHub Issues and Project board**; this file is the high-level narrative that keeps everyone oriented.
>
> PMs: replace the placeholder rows below with your real deliverables. Keep each deliverable small enough to become one or a few issues.

## Milestones at a glance

| # | Deliverable | Description | Owner (role) | Target |
|---|-------------|-------------|--------------|--------|
| 1 | Project scoping | Define the problem, success criteria, and out-of-scope items. | PM | Week 1 |
| 2 | Data sourcing & access | Identify and secure the data sources (see [`DATA.md`](DATA.md)). | PM + members | Weeks 1–2 |
| 3 | Data exploration (EDA) | Load, profile, and document the data; surface quality issues. | Members | Weeks 2–3 |
| 4 | Data cleaning & prep | Reproducible pipeline from raw → analysis-ready. | Members | Weeks 3–4 |
| 5 | Baseline model / analysis | First end-to-end result to beat. | Members | Weeks 4–5 |
| 6 | Iteration & evaluation | Improve on the baseline; agree on evaluation metrics. | Members + PM | Weeks 5–7 |
| 7 | Findings & deliverable | Report / dashboard / model artifact for the audience. | Members + PM | Weeks 7–8 |
| 8 | Handoff & retro | Documentation, reproducibility check, lessons learned. | PM | Week 8 |

## Timeline (rough)

```
Week:   1     2     3     4     5     6     7     8
        |-----|-----|-----|-----|-----|-----|-----|
Scope   ██
Data          ████
EDA                 ████
Prep                      ████
Baseline                        ██
Iterate                              ████████
Deliver                                       ████
Retro                                              ██
```

## Working agreements

- **Each deliverable maps to one or more GitHub Issues.** The board is the source of truth; this file is the summary.
- **Dates are estimates.** When reality diverges, update the issue and, if the shift is material, this file. Don't let this file quietly go stale.
- **"Done" is defined per issue** via acceptance criteria — not by a date passing.
- **Reprioritize openly.** If a deliverable changes, a PM notes why in the issue so the decision is auditable.
