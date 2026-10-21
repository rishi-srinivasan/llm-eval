# llm-eval

A small, reproducible harness for evaluating coding models as **autonomous bug-fixing agents**. Each model is driven through the [OpenAI Codex CLI](https://github.com/openai/codex) inside an isolated Docker container, given a real historical bug from [pallets/click](https://github.com/pallets/click), and graded on whether its patch fixes the bug without breaking anything else.

For every attempt the harness records three things:

| Metric | Source |
|---|---|
| **Pass rate** | Original test suite + withheld regression tests, both must pass |
| **Total time to complete the task** | Wall-clock time of the `codex exec` run |
| **Total tokens consumed** | Provider-reported usage from Codex's `turn.completed` events (input, cached input, output) |

Time to first token (TTFT) is measured separately with `ttft.py`.

The first model evaluated is **GLM-5.3 Flash** served through Ollama Cloud. The harness also supports an OpenAI model (`gpt-5.6-luna`) for side-by-side comparison.

## How it works

```
tasks.json ──► snapshot of Click at the buggy commit
                       │
                       ▼
        ┌──────────────────────────────┐
        │ Docker container (click-eval)│   model ⇄ Codex CLI ⇄ shell tools
        │ Codex sandbox, no web search │   (grep, edit files, run pytest)
        └──────────────┬───────────────┘
                       │ git diff of src/
                       ▼
   clean snapshot + model patch ──► network-less grading containers
        1. original tests (regression guard)
        2. withheld task-specific regression tests
                       │
                       ▼
           results.jsonl  ──►  report.md
```

- **Same harness for every model.** Tool calling, the agent loop and sandboxing are all handled by Codex; only the model and provider change (`MODELS` in [eval.py](eval.py)).
- **Isolation.** The agent runs in a container built from [Dockerfile](Dockerfile) (pinned Python, Codex and pytest versions). Codex's own sandbox runs in `workspace-write` mode with network access and web search disabled ([config.toml](config.toml)).
- **Hidden tests.** The model is told the bug and may run the existing tests, but the grading tests (`tasks/<id>/test_regression.py`) are never placed in its workspace. Only the diff under `src/` is graded, so edits to tests or configuration cannot affect the result.
- **Validated tasks.** `eval.py validate` checks that for every task the buggy base fails the regression tests while the upstream fix passes both test sets.
- **No silent retries.** Existing attempts on disk are skipped, and infrastructure or model errors are recorded as such rather than rerun.

## Tasks

Six real bugs from Click's issue tracker, each pinned to the commit before the upstream fix. Prompts give a minimal reproducer and the required behaviour; they do not reveal the fix.

| Task | Click issue | Reference PR | Difficulty | What the model must fix |
|---|---|---|---|---|
| `echo-empty-bytes` | [#3487](https://github.com/pallets/click/issues/3487) | [#3493](https://github.com/pallets/click/pull/3493) | small | `click.echo(b"")` raises `TypeError` instead of writing a newline |
| `usage-no-args` | [#3360](https://github.com/pallets/click/issues/3360) | [#3434](https://github.com/pallets/click/pull/3434) | small | `HelpFormatter.write_usage` with no arguments emits a blank line instead of `Usage: program` |
| `enum-choice-completion` | [#3015](https://github.com/pallets/click/issues/3015) | [#3471](https://github.com/pallets/click/pull/3471) | medium | Shell completion for `Enum`-backed `Choice` suggests names the parser rejects |
| `optional-option-value` | [#3084](https://github.com/pallets/click/issues/3084) | [#3152](https://github.com/pallets/click/pull/3152) | medium | Options with `is_flag=False` and a `flag_value` must accept zero or one explicit value |
| `parameter-source` | [#3458](https://github.com/pallets/click/issues/3458) | [#3484](https://github.com/pallets/click/pull/3484) | larger | `ctx.get_parameter_source()` must be available during parameter processing |
| `resource-exception` | [#2447](https://github.com/pallets/click/issues/2447) | [#3058](https://github.com/pallets/click/pull/3058) | larger | `Context.with_resource` must forward exception info to the resource's `__exit__` |


## Results: GLM-5.3 Flash

Run `glm-cloud`: GLM-5.3 Flash via Ollama Cloud, driven by Codex 0.163.0, provider-default reasoning effort, 3 repetitions of each of the 6 tasks (18 attempts).

**Overall: 16 / 18 attempts passed (89%).**

| Task | Passed | Mean time (s) | Mean tokens (input + output) |
|---|---|---|---|
| echo-empty-bytes | 3/3 | 106 | 581k |
| optional-option-value | 3/3 | 76 | 672k |
| parameter-source | 3/3 | 162 | 1,107k |
| resource-exception | 3/3 | 164 | 948k |
| usage-no-args | 2/3 | 82 | 270k |
| enum-choice-completion | 2/3 | 137 | 732k |

Per-attempt distribution (median, min–max):

| Metric | Value |
|---|---|
| Wall time | 114 s (55–228) |
| Input tokens | 684k (157k–1.53M), of which ~94% cached |
| Output tokens | 9.1k (3.1k–20.4k) |
| Input + output tokens | 695k (160k–1.55M) |

Agent activity across the 18 attempts: 488 shell commands executed through Codex, 436 reasoning items, and 18 final summaries.

**Time to first token** (`ttft.py`, direct streaming call with the task prompt, 2 repetitions, median): about **0.65–0.8 s** to the first token of any kind, and about **0.7–1.3 s** to the first non-reasoning content token.

**Failures.** Both misses (`usage-no-args` rep 2, `enum-choice-completion` rep 3) produced patches that applied cleanly and passed the original test suite but failed the withheld regression tests, i.e. incomplete fixes rather than crashes or regressions. Together they consumed about 1.14M tokens over 224 s.

Per-attempt grades are in [results/glm-cloud/results.jsonl](results/glm-cloud/results.jsonl), the model patches in `results/glm-cloud/<task>/<attempt>/patch.diff`, and the generated summary in [results/glm-cloud/report.md](results/glm-cloud/report.md). Full agent transcripts are not committed; rerunning produces them locally.

### Caveats

- GLM-5.3 Flash is a 321B-parameter model available in Ollama only as a cloud model, so these numbers include network latency and provider queueing; they are not local-inference speeds.
- Reasoning effort is the provider default, so budgets are not matched against other models.
- Tokens are provider-reported and tokenizers differ between models; compare token counts across providers with care.
- Codex reports 0 reasoning tokens for GLM via Ollama's Responses endpoint even though reasoning items are emitted, so reasoning cost is folded into other counts or unreported.
- Six tasks and three repetitions is a small sample (one run is 5.6 percentage points), and these are historical bugs that may appear in training data. The results are not a general capability claim.
- TTFT is measured outside Codex, so it reflects model and network latency only.

## Reproducing

Requirements: Docker, Python 3.10+, [Codex CLI](https://github.com/openai/codex), and [Ollama](https://ollama.com) signed in to an account with access to `glm-5.3-flash:cloud`.

```bash
# 1. Build the agent image
docker build -t click-eval .

# 2. Generate Codex's Ollama model catalog (copied into each container)
ollama launch codex --model glm-5.3-flash:cloud   # creates ~/.codex/ollama-launch-models.json

# 3. Verify every task: base fails, reference patch passes (first run downloads Click into .cache/)
python eval.py validate

# 4. Run GLM-5.3 Flash: 3 repetitions of all 6 tasks
python eval.py run glm-cloud --models glm --reps 3

# 5. Summarise pass rate, time and tokens
python eval.py report glm-cloud

# 6. Measure time to first token
python ttft.py --model glm-5.3-flash:cloud --reps 2 --max-tokens 1024
```

Useful flags for `eval.py run`: `--models luna,glm`, `--tasks echo-empty-bytes,usage-no-args`, `--reps N`, `--timeout SECONDS`. Running with `--models luna,glm` alternates which model goes first on each task to reduce ordering effects; the `luna` runs require Codex to be logged in to OpenAI.

To use the same model interactively with Codex outside the harness: `ollama launch codex --model glm-5.3-flash:cloud`.

## Repository layout

```
eval.py              runner: validate / run / report
ttft.py              time-to-first-token and token counts via streaming API
tasks.json           task metadata (issue, PR, base/fixed commits, difficulty)
tasks/<id>/          prompt.md, reference.patch, test_regression.py (withheld from the agent)
config.toml          Codex configuration used inside the container
Dockerfile           pinned agent/grading image
results/<run>/       results.jsonl, report.md, <task>/<attempt>/patch.diff (transcripts stay local)
```
