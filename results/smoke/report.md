# Report: smoke

Median (min-max). Tokens are provider-reported (different tokenizers); n/a = not reported.

## Passes by task

| task | glm |
|---|---|
| smoke | 1/1 |

## Overall, time, tokens (all attempts incl. failures)

| model | passes | status counts | wall s | input | cached | output | reasoning | total out+in |
|---|---|---|---|---|---|---|---|---|
| glm | 1/1 | {'ok': 1} | 12 (12-12) | 99,552 (99,552-99,552) | 94,272 (94,272-94,272) | 681 (681-681) | 0 (0-0) | 100,233 (100,233-100,233) |

## Tasks solved at least once by every model: ['smoke']

| model | wall s | output tokens |
|---|---|---|
| glm | 12 (12-12) | 681 (681-681) |

## Failed attempts: resource use

| model | failed | wall s total | input+output total |
|---|---|---|---|
| glm | 0 | 0 | 0 |

Effective settings: luna = low reasoning; glm = provider default (ollama reports default `max`). Budgets are not equivalent.
GLM runs on Ollama Cloud (not local inference). Six tasks, historical bugs possibly in training data; not a general capability claim.
