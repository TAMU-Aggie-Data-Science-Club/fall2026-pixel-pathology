# Contributing Guide

This is the playbook for running an **IDE Data Science Club** project on GitHub. It is **not** a general Git tutorial — it assumes you can already commit and push. What it explains is *how we work together in this repo*: who does what, how work flows from an idea to `main`, and which Git commands you reach for at each step.

Read your role's section first. Everyone should read [The Flow](#the-flow-issue--main) and [Staying in Sync](#staying-in-sync) — they apply to all of us.

> **Two roles, one repo.** **Project Managers (PMs)** are *managers*: they turn goals into issues, review pull requests, and are the only people who approve merges to `main`. **Members** are *developers*: they take an issue, build it on a branch, open a pull request, respond to review, and merge their work up the tree. If you are an AI agent working in this repo, also read [`AGENTS.md`](AGENTS.md) — it is the strict machine-facing version of this same workflow.

> **Companion files.** This guide links to other template files — [`AGENTS.md`](AGENTS.md), [`README.md`](README.md), [`DELIVERABLES.md`](DELIVERABLES.md), [`DATA.md`](DATA.md), and the [`data/`](data/) folder. They are part of the template and are populated as the repo is set up (each lands through its own issue and PR, exactly as described below). If a link 404s, that file simply hasn't been merged to `main` yet — it will be before the template is complete.

---

## Table of Contents

1. [The mental model](#the-mental-model)
2. [The flow: issue → `main`](#the-flow-issue--main)
3. [Staying in sync](#staying-in-sync)
4. [For Members (developers)](#for-members-developers)
5. [For Project Managers (managers)](#for-project-managers-managers)
6. [Branch naming](#branch-naming)
7. [Worktrees: one issue, one tree](#worktrees-one-issue-one-tree)
8. [Git commands in context](#git-commands-in-context)
9. [Code-review agents (strongly recommended)](#code-review-agents-strongly-recommended)
10. [Golden rules](#golden-rules)

---

## The mental model

Every change starts as a **GitHub Issue** (the *why*) and ends as a **merge into `main`** (the *done*). In between, work lives on branches organized as a small **tree**:

```
main                         ← protected. Only PMs merge here.
 └── issue-42/integration    ← one "root" branch per issue (the trunk of this issue's tree)
      ├── issue-42/loader     ← a feature branch: one cohesive piece of the issue
      └── issue-42/charts      ← another feature branch, worked in parallel
```

- **`main`** is the source of truth. It should always be in a known-good state. Nobody pushes to it directly.
- **An integration (root) branch** is created per issue. It collects all the work for that issue and is the **only** branch that opens a pull request into `main`.
- **Feature branches** hang off the integration branch. Each is one small, reviewable slice. They merge *up* into the integration branch, not into `main`.

Work flows **up the tree**: feature → integration → `main`. Reviews happen at every step. When `main` finally receives the integration branch, the whole team is back on the same page.

---

## The flow: issue → `main`

This is the loop the whole project runs on. Every deliverable in this repo — including this file — went through it.

1. **Open an Issue.** Describe the problem, the goal, and a checklist of acceptance criteria. No issue, no work.
2. **Cut the tree.** From the latest `main`, create the issue's integration branch, then a feature branch (in its own worktree) for the slice you're building.
3. **Build the slice.** Small, focused commits. Push early so others can see progress.
4. **Open a Pull Request** from your feature branch into the **integration branch** (not `main`).
5. **Review.** Wait for the code-review agent (if enabled) and for a human reviewer. Address the comments.
6. **Merge up.** Once approved, merge the feature branch into the integration branch. Repeat 2–6 for each slice.
7. **PM reviews the integration branch → `main`.** When every slice for the issue has merged into the integration branch, a PM does the final review and merges to `main`.
8. **Clean up.** Delete merged branches (local + remote) and remove the worktree. **History is preserved by the merge commits** — deleting the branch label does not delete the commits.
9. **Close the Issue** (a merged PR that says `Closes #42` does this automatically).

---

## Staying in sync

**This is the most common source of pain, so do it reflexively.** GitHub is the source of truth, not your laptop. Before you start any work — and regularly while you work — pull the latest:

```sh
git switch main
git pull origin main          # fast-forward your local main to match GitHub
```

When you cut a new branch, cut it from an **up-to-date** `main`. If your feature branch has fallen behind the integration branch while you were building, bring it forward before opening/updating your PR (see [rebase vs. merge](#git-commands-in-context)).

If you skip this, you will build on stale code and hit avoidable merge conflicts. **When in doubt, `git fetch` and look before you leap:**

```sh
git fetch origin              # update your view of every remote branch (changes nothing local)
git status                    # are you ahead/behind? clean/dirty?
```

---

## For Members (developers)

You own the *building*. Your job is to turn one issue's slice into a clean, reviewed PR.

**1. Pick up an issue.** Assign it to yourself on GitHub so no two people duplicate work. Read the acceptance criteria — that's your definition of done.

**2. Sync, then branch off `main`.**
```sh
git switch main && git pull origin main
git switch -c issue-42/integration        # create the issue's trunk (if it doesn't exist yet)
git push -u origin issue-42/integration
```

**3. Create a worktree for your slice** (see [Worktrees](#worktrees-one-issue-one-tree)):
```sh
git worktree add -b issue-42/loader ../PM_REPO_TEMPLATE.worktrees/loader issue-42/integration
```

**4. Build in small commits.** Each commit should be one coherent step, with a message that says *why*, not just *what*.

**5. Push and open a PR into the integration branch:**
```sh
git push -u origin issue-42/loader
gh pr create --base issue-42/integration --fill
```
Write a description a reviewer can act on: what changed, what you deliberately left out, and how you verified it.

**6. Respond to review.** Read the whole review before touching anything. Fix what's clearly right yourself; only ask the PM when there's a real judgment call (naming, scope, product behavior). Push follow-up commits and re-request review.

**7. Merge up** once approved (feature → integration), then delete your feature branch and remove the worktree. Move to the next slice.

**You are also a reviewer.** When a teammate requests review, read their PR and leave comments. Reviewing is half the job of being a developer here — it's how we catch bugs before `main` and how everyone learns the codebase.

---

## For Project Managers (managers)

You own the *coordination and the gate to `main`*. You mostly work in GitHub's UI, not the terminal.

**1. Turn goals into Issues.** Break the project (see [`DELIVERABLES.md`](DELIVERABLES.md)) into issues small enough for one person to finish in a few days. Give each a clear title, acceptance-criteria checklist, and labels. Assign or let members self-assign.

**2. Maintain the board.** Keep issues triaged and prioritized so members always know what to pick up next. Link related issues; close duplicates.

**3. Review pull requests.** This is your core review responsibility:
   - Feature → integration PRs can be reviewed by any member or by you.
   - **The integration → `main` PR is yours to review and merge.** Confirm every slice landed, the code-review agent passed, and the acceptance criteria are met.

   Use GitHub's review tools deliberately: **Comment** to ask questions, **Request changes** to block until fixed, **Approve** to sign off. Review the *diff*, not the whole repo.

**4. Gatekeep `main`.** Only you merge to `main`, and only after the integration branch is green and reviewed. Never enable auto-merge on a PR targeting `main`. Prefer **branch protection** on `main` (require a PR + at least one approval) so the rule is enforced, not just trusted.

**5. Keep the team in sync.** After a merge to `main`, remind members to `git pull origin main` before continuing — anyone behind is building on outdated code.

**6. Own the subjective calls.** Members escalate product/UX, naming, dependencies, and architecture decisions to you. Decide, and record the decision in the issue or PR so it's auditable.

---

## Branch naming

Namespace every branch by its issue number so the tree is obvious at a glance:

```
issue-<n>/integration        # the root/trunk branch for issue <n>
issue-<n>/<slice-slug>        # a feature/slice branch off the integration branch
```

**One hard rule:** inside an `issue-<n>/` namespace, every branch name is a **flat leaf** — no branch name may be a *prefix* of another. Git stores refs as files, so a branch named `issue-1/guide` makes it **impossible** to also create `issue-1/guide/body` (you'll get `cannot lock ref ... 'issue-1/guide' exists`). Use `issue-1/guide` and `issue-1/guide-body` instead.

---

## Worktrees: one issue, one tree

A **worktree** lets you check out multiple branches into **separate folders at the same time**, all backed by the one repository. That's how you build a feature slice without disturbing `main` (or another slice) in your main folder.

```sh
# create a new branch AND a folder for it, based off the integration branch
git worktree add -b issue-42/loader ../PM_REPO_TEMPLATE.worktrees/loader issue-42/integration

# work in that folder like a normal clone
cd ../PM_REPO_TEMPLATE.worktrees/loader
# ...edit, commit, push...

# see all active worktrees
git worktree list

# when the branch is merged and the folder is no longer needed
git worktree remove ../PM_REPO_TEMPLATE.worktrees/loader
```

Why we use them: parallel slices of one issue can each have their own folder, so switching contexts is `cd`, not `git stash` + `git switch`. The whole set of branches under `issue-42/` is that issue's **tree**, and it collapses back into `issue-42/integration` as slices merge up.

---

## Git commands in context

Reach for these at the moments described — not as isolated trivia.

- **`git fetch origin`** — *"What has changed on GitHub?"* Updates your remote-tracking view without changing your files. Safe anytime; do it before deciding whether you're behind.
- **`git pull origin main`** — *"Bring my local `main` up to date."* Fetch + merge in one step. Run before cutting a branch.
- **`git push -u origin <branch>`** — *"Publish my branch."* The `-u` sets upstream so later `git push`/`git pull` need no arguments.
- **`git rebase <base>`** — *"Replay my commits on top of the latest base."* Use it to bring a feature branch forward onto an updated integration branch so your PR is a clean, linear diff. **Only rebase branches that are yours and not yet merged.** Rebasing shared history rewrites commits others may have — don't.
  ```sh
  git switch issue-42/loader
  git fetch origin
  git rebase origin/issue-42/integration
  ```
- **`git merge`** — *"Combine another branch into this one, preserving both histories."* This is how work moves **up the tree** (feature → integration → `main`). We keep merge commits so the small-commit trail stays auditable.
- **`git reset`** — *"Move my branch pointer / unstage things."* Use `git reset --soft HEAD~1` to undo the last *local* commit but keep the changes, or `git restore --staged <file>` to unstage. **Never `git reset --hard` on work you haven't backed up, and never rewrite commits you've already pushed to a shared branch.**
- **`--force` / `--force-with-lease`** — avoid. Only ever force-push a branch that is exclusively yours, and prefer `--force-with-lease` so you don't clobber someone else's push. If you feel you need to force-push a shared branch, stop and ask a PM.

> If a rebase or merge produces conflicts: don't panic. Open the conflicted files, resolve the `<<<<<<<`/`=======`/`>>>>>>>` markers, `git add` them, and continue (`git rebase --continue` or commit the merge). If it's a mess, `git rebase --abort` / `git merge --abort` puts you back where you started.

---

## Code-review agents (strongly recommended)

We **strongly recommend** enabling an automated code-review agent on this repo — **Codex auto-review** (`chatgpt-codex-connector`) or **Claude auto-review**. We do not ship one in this template (you install it on the repo/org), but a project runs much more smoothly with one.

Why it's worth it:
- Every PR gets a fast, consistent first pass **before** a human spends time on it.
- Members get immediate feedback and learn from it; PMs review higher-quality diffs.
- It catches the boring class of bugs (typos, missed edge cases, obvious mistakes) so human review can focus on design and correctness.

How it fits the flow: when a PR opens, the agent reviews it automatically and signals when it's done (Codex reacts on the PR body; a re-review after new commits is requested with a `@codex review` comment). **Wait for that signal, address the findings, then merge up.** The agent is an assistant, not the gate — a human still reviews, and a PM still owns the merge to `main`.

---

## Golden rules

- **No work without an issue.** The issue is the *why*.
- **Never push to `main`.** It moves only through a reviewed PR merged by a PM.
- **Sync before you branch.** Cut from an up-to-date `main`; pull often.
- **Small slices, small PRs.** If a PR is sprawling, split it.
- **Merge up the tree** with merge commits — feature → integration → `main`.
- **Review each other's work.** Everyone is a reviewer.
- **Don't rewrite shared history.** No force-push / hard-reset on branches others use.
- **Delete merged branches, keep the commits.** Clean tree, full history.
