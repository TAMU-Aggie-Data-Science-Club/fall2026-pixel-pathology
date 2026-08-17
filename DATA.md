# Data

This file explains the project's **data sources** — where they come from, how to get them, and how to think about using them. It is the contextual companion to the [`data/`](data/) folder.

> **`DATA.md` is tracked in git. The `data/` folder is not.** Documentation about the data lives here, in version control, so the whole team shares one understanding. The datasets themselves live in `data/`, which is **git-ignored** — raw data is often large, private, or licensed, and must never be committed. Clone the repo, then populate `data/` locally by following the sources below.

## Where to look for sources

At the start of the project, before committing to a source, scan these in roughly this order:

1. **A source the club or a sponsor already provides.** If the project came with data, that's your primary source — document it first.
2. **Official / authoritative open data.** Government portals (e.g. data.gov), inter-governmental bodies, and official statistics agencies. Highest trust, usually well-documented, clear licensing.
3. **Curated dataset hubs.** Kaggle, Hugging Face Datasets, UCI ML Repository, Google Dataset Search, AWS/Azure open-data registries. Fast to start with; check the license and provenance.
4. **Domain-specific repositories / APIs.** Whatever is standard for the project's field (e.g. a scientific archive, a public API, a research consortium). Often the richest and most relevant.
5. **First-party collection.** Surveys, scraping (only where permitted), or instrumentation you build. Highest effort and the most responsibility — get PM sign-off first.

## How to think about using a source (high level)

Before you rely on a dataset, a member should be able to answer these — and record the answers in the source's row below:

- **License & permission.** Are we allowed to use it for this purpose, and to share results? If unclear, ask a PM before building on it.
- **Provenance.** Who produced it, when, and how? Freshness and collection method shape what conclusions are valid.
- **Fitness.** Does it actually measure what the project needs? Coverage, granularity, and sample size matter more than size.
- **Sensitivity.** Any PII, confidential, or ethically sensitive content? If yes, that dictates storage and handling — and it stays out of git regardless.
- **Reproducibility.** Can a teammate re-fetch it from your notes alone? If not, the source isn't documented well enough yet.

Choosing and vetting a source is a **judgment call** — surface it to a PM rather than deciding a major data direction alone.

## Source register

Document every source here as you adopt it. Replace these placeholders.

| Source | Origin / URL | Access method | License | Sensitivity | Notes |
|--------|--------------|---------------|---------|-------------|-------|
| _e.g. Example Open Dataset_ | `https://…` | Manual download → `data/raw/` | CC-BY-4.0 | None | Updated annually |
| | | | | | |

## Local layout convention

The `data/` folder is git-ignored, but keep a consistent structure inside it so everyone's local copy matches:

```
data/
├── raw/          # exactly as downloaded — never edit by hand
├── interim/      # partially processed, intermediate outputs
└── processed/    # analysis-ready, produced by the cleaning pipeline
```

Because `data/` isn't in git, the **pipeline that fetches and builds these folders** is what must be committed and reproducible — not the data itself.
