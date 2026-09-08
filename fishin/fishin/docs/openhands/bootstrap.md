# OpenHands Bootstrap

## Current status

The repository designates OpenHands as its execution harness. GitHub remains the durable source of truth, and the model API is a replaceable external dependency. The preferred initial path is:

```text
GitHub Issue -> OpenHands -> OpenAI-compatible gateway -> open-weight model
```

No OpenHands package, CLI, credential, or provider-specific application dependency is committed here.

## Configuration boundary

Credentials are BYOK. The CEO must supply them through the secure configuration mechanism supported by the selected OpenHands installation. Credentials must not be committed to Git, documentation, Issues, PRs, repository configuration, or logs.

The model identifier, gateway, and provider route must remain operator-supplied configuration rather than source-code constants. This repository intentionally does not provide an `.env.example` until the supported OpenHands installation and its exact configuration variable names are verified.

## Bootstrap blocker

At the time of this change, the execution environment has no discoverable `openhands` command and no installed OpenHands package or SDK. The repository also contains no retained, authoritative OpenHands configuration documentation. Therefore this change does not invent a CLI command, package name, configuration schema, or model route.

Before autonomous execution can be enabled, the CEO or operator must:

1. Choose and install a supported OpenHands release using its official documentation.
2. Configure a private API key and an OpenAI-compatible model endpoint through that installation's supported mechanism.
3. Confirm the selected model route is affordable/free under the $0 constraint.
4. Run the smoke procedure below and record the exact installation/configuration commands privately, without committing secrets.

## Required smoke procedure

Run the procedure only after OpenHands is installed and configured:

1. Start OpenHands against this repository.
2. Confirm it reads `AGENTS.md`, `PROJECT.md`, `VISION.md`, `STRATEGY.md`, `ROADMAP.md`, `GOALS.md`, `STATE.md`, and `DECISIONS.md`.
3. Ask it to inspect `agent_system/context.py` without changing Python code.
4. Ask it to make a harmless documentation-only change on a disposable branch.
5. Run:

   ```text
   python -m pytest -q
   python -m compileall -q agent_system tests
   ```

6. Inspect the diff for malformed Python, credential exposure, unexpected files, and scope expansion.
7. Discard the disposable change unless it is an explicitly authorized Issue deliverable.
8. Record whether startup, context loading, editing, testing, compilation, and reporting all completed cleanly.

This procedure is intentionally a checklist rather than an invented OpenHands command sequence. Its executable commands depend on the verified OpenHands release and are not known in the current environment.
