# Contributing to Bento

Thanks for your interest in contributing to **Bento**, a genomics data orchestration service developed by the [Canadian Centre for Computational Genomics](https://computationalgenomics.ca/).

Bento is a collection of microservices distributed across multiple sub-repositories. Most contribution workflows are similar across repos, but some details (setup, tests, linting) live in each sub-repo's own `README`. This document covers the conventions that apply platform-wide.

## Code of Conduct

This project and everyone participating in it is expected to abide by a code of conduct. We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold its terms. Report unacceptable behavior to the maintainers.

## Getting Started

### Development environment

To work on Bento or any of its services, start by installing Bento itself — you do not need to clone individual service repositories first. Follow the instructions in this repository's [README](./README.md).

If you want to work on a specific service, see the [development guide](https://github.com/bento-platform/bento/blob/main/docs/development.md). Then refer to that service repository's `README.md` for further instructions.

### Running tests and linters

Each sub-repository defines its own testing and linting setup. Check the relevant `README.md` and the GitHub Actions workflows in `.github/workflows/` to see exactly which commands are run in CI — your local checks should match those.

## Finding Something to Work On

Internal contributors track work in **Redmine**. Before starting on something:

1. Find or create a ticket in Redmine that describes the work.
2. Assign the ticket to yourself.
3. Keep the status and `% completed` up to date (e.g., *In Progress*, *In Review*, *Closed*) as you progress.

This keeps the team aware of who is working on what and avoids duplicated effort.

## Making Changes

### Branch naming

Use descriptive, prefixed branch names. Recommended conventions:

- `feature/<short-description>` — new functionality
- `fix/<short-description>` — bug fixes
- `refactor/<short-description>` — refactors
- `chore/<short-description>` — tooling, dependency bumps
- `docs/<short-description>` — documentation-only changes

Including the Redmine ticket ID is encouraged, e.g. `feature/1234-add-search-endpoint`.

### Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/). Each commit message should look like:

```
<type>(<optional scope>): <short description>

<optional body>

<optional footer>
```

Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`, `perf`.

Examples — committing in the main `bento` repository, where the scope is the affected service:

```
feat(katsu): add phenopacket v2 ingest endpoint
fix(gohan): handle empty VCF gracefully
docs: clarify bentoctl installation steps
```

Examples — committing inside a sub-service repository (e.g. `katsu`), where the scope is the affected internal module or app:

```
feat(phenopacket): add compound key of individual id and dataset id to support multiple phenopacket imports
test(chord): add tests for dataset ingestion
```

### Code style

Each sub-repository specifies its own formatter and linter. Use the tool configured in that repo, and check the repo's GitHub Actions lint workflow to ensure your changes pass the same checks CI will run. If a pre-commit hook or formatter config (e.g., `pyproject.toml`, `.eslintrc`, `.prettierrc`) is present, use it.

## Pull Requests

### Opening a PR

- Open the PR against the appropriate base branch (usually `main`). In the main `bento` repository, active development targets the current release branch (e.g., `releases/v24`) — check with your team if unsure.
- Use a clear, conventional-commit-style title (e.g., `feat(<scope>): add X` or `fix: handle Y`).
- In the description, include:
  - A short summary of the change and why it's needed.
  - A link to the relevant Redmine ticket.
  - Notes on anything reviewers should pay extra attention to (migrations, breaking changes, config updates).
  - Testing notes — what you ran and what you observed.
- Keep PRs focused. Smaller, single-purpose PRs are easier to review and merge.

### Reviews

Pick reviewers based on context:

- Anyone who has recently worked on or owns the affected area of the codebase.
- Anyone else whose input you think is relevant (domain knowledge, dependent service owners, etc.).

At least one approval is required before merging. For larger or cross-cutting changes, get an additional reviewer.

**As a reviewer:**

- Aim to review within 1–2 business days of being assigned.
- Distinguish blocking from non-blocking comments. Prefix non-blocking suggestions with `nit:` or `optional:` so the author knows they can merge without resolving them.
- Use "Request changes" for issues that must be fixed before merging. Use "Comment" for questions or non-blocking feedback. Use "Approve" when you're satisfied the PR is ready.

### CI and merging

- All CI checks (tests, linters, builds) **must pass** before a PR can be merged.
- Address review comments before re-requesting review.
- **Merge commit** is the default merge strategy. Individual commits are preserved in the history.

## Reporting Bugs, Requesting Changes, and Security Issues

To report a bug, request a change, or report a security issue, please use this form:

👉 [Bug/security report form](https://forms.gle/gtihcUDUpa64b14R6)

For security issues, please **do not** open a public GitHub issue. The form is the right channel — it lets us triage and respond privately before any disclosure.

## Licensing of Contributions

Bento is licensed under the [GNU Lesser General Public License v3.0 (LGPL-3.0)](./LICENSE). By submitting a contribution, you agree that your contribution will be licensed under the same LGPL-3.0 terms.

If you are contributing on behalf of an organization, make sure you have the authority to do so.

---

Thanks for helping make Bento better! 🎉