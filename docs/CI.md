# CI for Agent Hive

CI means continuous integration: automatic checks run when code is pushed or a pull request is opened or updated. The workflow is `.github/workflows/ci.yml`.

## What runs now

- Required starter documents must exist and contain data.
- Tracked `AGENTS.local.md` files are rejected; their absence is normal and does not fail CI.
- Tracked `.env` files (except `.env.example`) and common local dependency/build directories are rejected.
- Git checks changed lines for whitespace errors, including trailing spaces and conflict markers it recognizes.

This is a bootstrap workflow, not application validation or a comprehensive security scanner. It needs no repository secrets, API keys, database, npm packages, or pip packages. It uses Python already provided on the GitHub-hosted Ubuntu runner for a short filename check.

## Why these choices

| Choice | Reason | Alternative |
|---|---|---|
| GitHub Actions | Runs alongside the existing GitHub repository. | A separate CI service adds setup without a current requirement. |
| Push and pull-request triggers | Checks work on branches and proposed merges. Some branch PRs can produce two runs. | PR-only saves runs but does not check a branch before a PR exists. |
| Manual trigger | Allows rerunning a workflow intentionally once available on the default branch. | Push a new commit, which is unnecessary for a rerun. |
| Read-only contents permission | The workflow only needs to read source. | Write access is unnecessary here. |
| Checkout without persisted credentials | Later shell steps do not need Git credentials. | Default persisted credentials are useful for workflows that intentionally push changes. |
| Full history | Allows checking the actual push/PR range. | Shallow fetch saves bandwidth but needs extra base-fetch logic. |
| Five-minute timeout and cancellation | Stops stuck or superseded checks from wasting runner time. | Let every outdated run finish. |
| Required-file shell loop | Easy to understand; fails on absent/empty documents. | A larger validation framework offers little benefit at this stage. |
| Python path checks | Handles filenames reliably and checks what Git actually tracks. | Complex shell matching is harder to read and can mishandle unusual names. |
| Patch whitespace check | Built into Git; requires no formatting dependency. | A documentation formatter could be added if the team wants one later. |

The Python snippet gets tracked filenames from `git ls-files`, separates them at null characters, checks each filename/path, and exits with a nonzero code when blocked local files are tracked. It does not inspect file contents or determine whether a value is a secret. `.gitignore` prevents accidental additions, while CI also catches files explicitly forced into Git.

The whitespace step uses the PR base for pull requests, the previous pushed commit for ordinary pushes, and an empty Git tree for initial/new-branch/manual cases where an appropriate previous commit is absent. Event values are passed through environment variables rather than interpolated into shell code.

## Add real checks as the project grows

1. **First backend feature:** choose and pin a Python runtime and dependency set; add Ruff and pytest with meaningful tests for that feature. CI installs the committed dependency set, lints code, and runs tests. No collected tests should be treated as success once this job exists.
2. **Frontend setup:** choose a supported Node runtime and commit the package lock. Use `npm ci` and explicit lint, type-check, and build scripts. Fail when required scripts are missing; do not use optional scripts to silently skip checks.
3. **Persistence:** add an isolated PostgreSQL service in CI, apply migrations, and run database integration tests with test-only credentials.
4. **Sensitive actions:** add tests for missing consent, unauthorized approval, proposal expiry, duplicate execution, and booking conflicts.
5. **Evaluation:** keep paid real-model benchmarks outside routine PR CI; use deterministic mocks for regular tests.

Do not add deploy credentials or automatic production deployment at repository bootstrap. Branch protection and required status checks are repository settings: this file does not enable them. Once the workflow passes remotely, the repository owner can require its check before merging, where their GitHub configuration supports it.

## Verification

After committing the workflow to GitHub, open the repository's Actions tab and inspect the actual run. Local YAML parsing and shell checks do not establish that a hosted run passed. Test a deliberate whitespace or blocked-file error on a temporary branch if you want to see the failure behavior, then remove it before merging.

Official reference: https://docs.github.com/en/actions/get-started/quickstart

Member instruction files and submissions/private/ are also rejected if tracked. Shared *-progress.md records are intended to be committed.
