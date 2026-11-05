# ai-review-test

A small TODO REST API (Python / FastAPI) whose real purpose is to test **automated Claude Code
reviews on every pull request**, using [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action).

The app is split across several modules (routes, service, storage, models) so PRs touching it
give the reviewer something realistic to reason about.

## Repository layout

| Path | Purpose |
|---|---|
| `app/` | FastAPI application (`routes` -> `service` -> `storage`, plus `models`) |
| `tests/` | pytest suite (service unit tests + API tests) |
| `Dockerfile` | Production image (non-root, single uvicorn worker) |
| `CLAUDE.md` | Project conventions **and the review guidelines the reviewer follows** |
| `.github/workflows/claude-review.yml` | The PR review workflow |

## Run the app

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload     # http://localhost:8000/docs
```

Or with Docker:

```bash
docker build -t todo-app .
docker run --rm -p 8000:8000 todo-app
```

### API

| Method | Path | Description |
|---|---|---|
| `GET` | `/healthz` | Liveness check |
| `POST` | `/todos` | Create (`title`, optional `description`) |
| `GET` | `/todos?done=true\|false` | List, optionally filtered |
| `GET` | `/todos/{id}` | Fetch one |
| `PATCH` | `/todos/{id}` | Partial update (`title`, `description`, `done`) |
| `DELETE` | `/todos/{id}` | Delete |

Data is stored in memory and lost on restart.

## Automated Claude PR review

### How it works

On every PR opened, updated (new push), reopened, or marked ready for review, the
`Claude PR Review` workflow checks out the PR branch and runs Claude Code headlessly.
Claude reads `CLAUDE.md` for the review guidelines, inspects the diff with `gh pr diff`,
and posts inline comments plus one summary comment on the PR.

### Setup (one time)

1. Configure the model gateway under *Settings -> Secrets and variables -> Actions*:

   | Type | Name | Value |
   |---|---|---|
   | Secret | `ANTHROPIC_BASE_URL` | Base URL of your Anthropic-compatible gateway |
   | Secret | `GATEWAY_API_KEY` | Gateway bearer token (sent as `Authorization: Bearer ...`) |
   | Variable | `ANTHROPIC_MODEL` | Model name the gateway serves (used for the main model and Claude Code's small-model calls) |

   The workflow stops with a clear error if any of these are missing. If your gateway uses
   `x-api-key` instead of a bearer token, nothing else needs to change.
2. Install the [Claude GitHub App](https://github.com/apps/claude) on the repository.
   The action uses it to post comments. It only needs to be installed on the repo; it does not
   have to belong to the same Claude account as the gateway credentials.
3. Push this repo to GitHub, then open a PR from a branch **in the same repo**. The review runs
   automatically. Tune the behaviour by editing the "Code review guidelines" in `CLAUDE.md`
   or the `prompt` in the workflow.

### Guard rails built into the workflow

| Risk | Mitigation |
|---|---|
| Secret theft via malicious PR code | Uses the `pull_request` trigger, **not** `pull_request_target`. Fork PRs are skipped (they have no secrets anyway). |
| Prompt injection from PR title/body/diff | Prompt and `CLAUDE.md` treat PR content as untrusted data. Claude is limited to `Read`, `Grep`, `Glob`, `gh pr comment/diff/view` and the inline-comment tool. No general Bash, no file edits. |
| Excess token permissions | Job permissions are `contents: read`, `pull-requests: write`, plus `id-token: write` (required by the action itself). |
| Cost and comment spam | Draft PRs are skipped, `concurrency` cancels an in-flight review when a new commit is pushed, `--max-turns 25`, `timeout-minutes: 15`, and the summary uses a single sticky comment. |

### Things to know

- Every push to an open PR triggers a new review and therefore a new API charge.
- Review output is non-deterministic. Treat it as an assistant, not a gate: the workflow
  does not fail the PR check based on findings.
- `claude-code-action` is referenced as `@v1` (a moving tag). For stricter supply-chain control,
  pin it to a full commit SHA.
