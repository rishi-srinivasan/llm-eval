# Report: glm-cloud

Median (min-max). Tokens are provider-reported (different tokenizers); n/a = not reported.

## Passes by task

| task | glm |
|---|---|
| echo-empty-bytes | 3/3 |
| enum-choice-completion | 2/3 |
| optional-option-value | 3/3 |
| parameter-source | 3/3 |
| resource-exception | 3/3 |
| usage-no-args | 2/3 |

## Overall, time, tokens (all attempts incl. failures)

| model | passes | status counts | wall s | input | cached | output | reasoning | total out+in |
|---|---|---|---|---|---|---|---|---|
| glm | 16/18 | {'ok': 18} | 114 (55-228) | 684,382 (157,056-1,526,748) | 642,496 (140,864-1,471,424) | 9,088 (3,102-20,415) | 0 (0-0) | 695,020 (160,158-1,545,461) |

## Tasks solved at least once by every model: ['echo-empty-bytes', 'enum-choice-completion', 'optional-option-value', 'parameter-source', 'resource-exception', 'usage-no-args']

| model | wall s | output tokens |
|---|---|---|
| glm | 114 (55-228) | 9,774 (3,102-20,415) |

## Failed attempts: resource use

| model | failed | wall s total | input+output total |
|---|---|---|---|
| glm | 2 | 224 | 1,140,587 |

Effective settings: luna = low reasoning; glm = provider default (ollama reports default `max`). Budgets are not equivalent.
GLM runs on Ollama Cloud (not local inference). Six tasks, historical bugs possibly in training data; not a general capability claim.
