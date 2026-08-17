# Deliverables & Timeline

> **How to read this file.** This is the PMs' best current estimate of what Pixel Pathology needs to ship and roughly when. It is a **living plan, not a contract**. The authoritative picture lives in **GitHub Issues and the Project board**.

## Milestones (suggested)

| # | Deliverable | Description | Owner (role) | Target |
|---|-------------|-------------|--------------|--------|
| 1 | Project scoping | Pick dataset. Define target task (binary vs. multi-class). Define success metric (AUC, recall on minority class). Write the "this is not a diagnostic tool" disclaimer. | PM | Week 1 |
| 2 | Data access | Register / download the chosen dataset. Document licensing constraints in [`DATA.md`](DATA.md). | PM + members | Week 1 |
| 3 | Data loader + splits | Reproducible train/val/test split by patient (not image) to prevent leakage. Augmentation pipeline. | Members | Weeks 2–3 |
| 4 | Baseline model | Frozen-backbone ResNet50 with a linear head. First result to beat. | Members | Week 3 |
| 5 | Fine-tuned model | Two-stage training (head → full network), regularization, class-balanced loss. | Members | Weeks 4–5 |
| 6 | Grad-CAM | Overlay implementation and sanity check on hand-picked examples (do heatmaps land where a human would look?). | Members | Weeks 5–6 |
| 7 | Streamlit demo | Upload → prediction + probability + Grad-CAM overlay + disclaimer. | Members + PM | Weeks 6–7 |
| 8 | Handoff & retro | Reproducibility check, short writeup with failure-mode examples, lessons learned. | PM | Week 8 |

## Timeline (rough)

```
Week:   1     2     3     4     5     6     7     8
        |-----|-----|-----|-----|-----|-----|-----|
Scope   ██
Access  ██
Loader        ████
Baseline            ██
Fine-tune                 ████
Grad-CAM                        ████
Demo                                       ████
Retro                                              ██
```

## Working agreements

- **Each deliverable maps to one or more GitHub Issues.** The board is the source of truth; this file is the summary.
- **Dates are estimates.** When reality diverges, update the issue and this file if the shift is material.
- **"Done" is defined per issue** via acceptance criteria — not by a date passing.
- **Reprioritize openly.** If a deliverable changes, a PM notes why in the issue so the decision is auditable.
