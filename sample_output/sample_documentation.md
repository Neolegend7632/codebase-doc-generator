```markdown
## Overview
This code implements a documentation generation pipeline specifically designed to analyze Python and JavaScript code, producing structured Markdown documentation. By utilizing a modular design with dedicated AI agents for analysis, documentation writing, and quality review, it ensures accurate and high-quality output while maintaining responsiveness through asynchronous programming.

## Installation & Dependencies
- `os`: For interacting with the operating system (no installation needed).
- `dotenv`: A library for loading environment variables from a `.env` file (install via `pip install python-dotenv`).
- `AsyncGenerator`: A typing hint from Python's built-in `typing` module; no installation required.

## API Reference

### Class: Agent
Represents an AI agent that performs specific roles in the documentation pipeline.
**Parameters:** Not explicitly defined due to its class nature.
**Returns:** None.
**Raises:** May raise errors if incorrect parameters are supplied.

### Function: run_pipeline
Asynchronously runs the documentation pipeline, generating complete Markdown documentation.
**Parameters:**
| Name     | Type | Description                                      |
|----------|------|--------------------------------------------------|
| code     | str  | The raw source code (either Python or JavaScript) to document. |
| language | str  | The programming language of the provided code, expected to be either 'Python' or 'JavaScript'. |
**Returns:** `str` — Complete polished Markdown documentation.
**Raises:** `ExceptionType` — May raise exceptions if the `Runner.run` calls encounter issues.

### Function: stream_pipeline
Similar to `run_pipeline`, but yields progress updates allowing real-time feedback to the user in the UI.
**Parameters:**
| Name     | Type | Description                                      |
|----------|------|--------------------------------------------------|
| code     | str  | The raw source code to document.                 |
| language | str  | The programming language of the source code.     |
**Returns:** `AsyncGenerator[str, None]` — Yields status updates and final documentation strings asynchronously.
**Raises:** `ExceptionType` — May raise exceptions when calling `Runner.run` if there are errors.

### Function: set_tracing_disabled
Disables tracing in the OpenRouter context.
**Parameters:**
| Name    | Type | Description                                      |
|---------|------|--------------------------------------------------|
| enabled | bool | A boolean that determines whether tracing is disabled. |
**Returns:** None.
**Raises:** None.

## Usage Examples
```python
# Usage of run_pipeline
result = await run_pipeline('def example(): pass', 'Python')
print(result)
# Expected output: Complete Markdown documentation for the function example
```

```python
# Usage of stream_pipeline
async for status in stream_pipeline('console.log("Hello, world!");', 'JavaScript'):
    print(status)
# Expected output:
# ⏳ Step 1 of 3 — Code Analyst is reading your code...
# ⏳ Step 2 of 3 — Documentation Writer is drafting the docs...
# ⏳ Step 3 of 3 — Quality Reviewer is checking and polishing...
# Final output: Complete Markdown documentation.
```

## Edge Cases & Gotchas
- An empty code string will result in immediate feedback indicating that no code was provided.
- Any errors raised during the processing of the `Runner.run` calls are not explicitly documented, potentially leading to silent failures.
- The design assumes correct identification and handling of Python and JavaScript code conventions, which could lead to unexpected results if other programming languages are provided.
```