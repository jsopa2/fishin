# Decisions

## 001 — Validate before productizing

We will validate the fishing prediction before building a polished consumer application.

## 002 — No assumption that ML is necessary

We will use the simplest model that performs well. Potential approaches include rules, statistical models, logistic regression, random forest, gradient boosting, and other ML. An LLM is not automatically the prediction model.

## 003 — $0 initial budget

Prefer free APIs, open datasets, open-source software, and free infrastructure.

## 004 — Human approval for major decisions

Agents may research, implement, test, and document. The CEO approves major product, architecture, financial, and strategic decisions.

## 005 — Evidence over appearances

The system must never represent an arbitrary score as scientifically validated.

## 006 — GitHub/Copilot as operating model instead of autonomous agents

The company operates via GitHub as the durable source of truth, with CEO setting objectives and Copilot executing disciplined work through GitHub Issues and PRs.

**Rationale:**
- GitHub is widely understood and provides version control, audit trail, and durable memory
- Human-in-the-loop model (CEO → Issues → Copilot → PRs → Approval → Merge) reduces risk of autonomous mistakes
- PR review and CEO approval gates ensure major decisions are visible and approved
- Moving away from OpenHands SDK simplifies dependencies and reduces framework lock-in
- Copilot executes focused, evidence-based work following lightweight role definitions (RESEARCH.md, DATA_SCIENCE.md, ENGINEERING.md, QA.md, DOCUMENTATION.md)
- No separate autonomous agent orchestration framework—Copilot is the single execution engine

## 007 — Issue-authorized routine execution

Routine work is authorized by a clearly scoped GitHub Issue. Copilot may implement, test, document, refactor, maintain CI, make ordinary task-required dependency updates, create PRs, respond to feedback, and merge after required checks pass when the work remains within the Issue scope.

CEO approval remains required for spending, paid services, material product or strategy changes, major unauthorized architecture changes, externally significant claims, material security or privacy decisions, sensitive-information exposure, abandoning major objectives, destructive actions, and other decisions requiring founder judgment.

This decision clarifies the operating model established by Decision 006: its historical emphasis on human review and approval applies to gated decisions, not every routine PR.

## 008 — OpenHands execution harness

OpenHands is the current execution harness for authorized GitHub Issue work. GitHub remains the durable company source of truth, and the model API is a replaceable external dependency. The initial preferred path is OpenHands through an OpenAI-compatible gateway such as OpenRouter to an open-weight model, subject to verified tool configuration and CEO-approved credentials.

This supersedes Decision 006's current-agent wording without rewriting its historical record. Governance, authorization boundaries, CEO approval gates, and evidence standards remain unchanged.
