# Workspace Instructions

## Scope

- This is a standalone test workspace.
- The remote `aiworkspace` repository is reference-only and is not a synchronization target.
- Project skills live under `.codex/skills/`.
- Do not modify the source skills under `C:\Users\Administrator\.codex\skills` while working in this workspace.

## Code Style

- Use English-only code comments.
- Prefer pure functions and functional composition.
- Use strict types and explicit return types.
- Validate required external data at runtime and ignore unrelated extra fields.
- Do not use default parameter values or boolean mode parameters.
- Follow DRY, KISS, and YAGNI.

## Errors and Testing

- Fail explicitly with specific exceptions.
- Do not silently ignore errors or add fallback behavior unless requested.
- Retry external API calls, log each retry as a warning, and raise the final error.
- Prefer smoke, integration, and end-to-end tests over mocks.
- Run relevant validation after changing scripts or skill contracts.

## Security

- Never commit tokens, passwords, database connection files, generated database metadata, or test output.
- Use `credentials.local.json`, `environments_config.json`, and skill-local ignored state for secrets.
- Database access should use read-only accounts unless a test explicitly requires controlled data mutation.
