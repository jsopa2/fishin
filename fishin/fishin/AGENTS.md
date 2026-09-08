# Company Constitution

Before meaningful work, agents must read `VISION.md`, `PROJECT.md`, `STRATEGY.md`, `ROADMAP.md`, `GOALS.md`, `STATE.md`, and `DECISIONS.md`.

## Rules

* Do not invent data or fabricate research findings.
* Do not claim accuracy without evidence.
* Prefer free/open data and simple solutions.
* Document assumptions and meaningful discoveries.
* Test meaningful code and keep changes focused.
* Avoid unnecessary dependencies or infrastructure.
* Do not expand scope without justification.

Agents may research, analyze data, write documentation, implement routine changes, test and fix straightforward failures, create pull requests, and propose follow-up work.

A clearly scoped GitHub Issue authorizes routine work within that Issue's scope, including implementation, tests, required documentation, ordinary refactoring, CI maintenance, ordinary dependency updates, PR creation, feedback response, and merging after required checks pass. A routine PR does not require separate CEO approval.

CEO approval is required before spending money, introducing paid services, making material product or strategy changes, making major unauthorized architectural changes, publishing externally significant claims, making material security or privacy decisions, exposing sensitive information, abandoning a major objective, or taking destructive or difficult-to-reverse actions. Copilot must stop before taking or merging a gated action and present the decision, rationale, proposed action, and evidence/risk.

Copilot must not silently expand an Issue's scope. Automated checks must pass, known secrets must not be exposed, and tests/checks must not be weakened to obtain a green build.

Completed work must report what was done, learned, evidence, tests, limitations, and a recommended next action. Blocked work must report the blocker, why, options, recommendation, and whether CEO approval is required.
