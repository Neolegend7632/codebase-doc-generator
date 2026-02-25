# Section 1 — Imports and Configuration

# Imports, tracing disabled, environment loaded

# The opening block of every file that uses the Agents SDK. We import what we need, disable tracing immediately, load the .env file, and configure OpenRouter. This is identical in purpose to Cell 1 of our notebooks — same rules, same order.

# Notice we also import AsyncGenerator from Python's built-in typing module. We use this in Section 6 to type-hint our streaming function — it tells Python and other developers exactly what kind of data that function yields.

# ================================================================
# app/agents.py
# The three-agent documentation pipeline.
# Called by app.py (the Gradio UI) — never run directly.
# ================================================================

import os
from dotenv import load_dotenv

# Agent  — defines one AI agent (name, instructions, model)
# Runner — executes an agent and returns its output
# set_tracing_disabled — silences 401 errors from OpenRouter usage
from agents import Agent, Runner, set_tracing_disabled

# AsyncGenerator — a type hint for functions that yield values
# asynchronously. Used to type our streaming function correctly.
from typing import AsyncGenerator

# Disable tracing FIRST — before any agent is created or run
set_tracing_disabled(True)

# Load .env so os.getenv() can find our API key and model setting
load_dotenv(override=True)

# Point the Agents SDK at OpenRouter instead of OpenAI
os.environ["OPENAI_API_KEY"]  = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

# Read the model name from .env — fallback to gpt-4o-mini if not set
MODEL = os.getenv("MODEL", "openai/gpt-4o-mini")




# Section 2 — Agent 1: Code Analyst

# Agent 1 — reads raw code, produces structured analysis

# The Code Analyst's job is purely to understand the code. It reads raw Python or JavaScript and extracts everything relevant — functions, classes, parameters, return types, dependencies, edge cases. It does not write documentation. It only produces a precise, structured analysis that the next agent can work from.

# Notice the system prompt explicitly tells the agent its output will be passed to a documentation writer. This shapes how it formats the analysis — structured, complete, no fluff.

# ── Agent 1: Code Analyst ─────────────────────────────────────────────────
#
# Job: read raw code → produce a structured analysis.
# Does NOT write documentation. Only analyses and extracts.
#
# We define agents at module level (outside any function) so they are
# created once when the file loads — not recreated on every pipeline run.
# This is more efficient and is standard Python practice.
code_analyst = Agent(
    name="Code Analyst",
    instructions="""
    You are an expert code analyst specialising in Python and JavaScript.
    Your job is to read code and produce a thorough, structured analysis.

    For EVERY function, method, and class in the code, identify and report:

    1. Name and purpose — what it does in plain English (1-2 sentences)
    2. Parameters — each parameter's name, type, and what it represents
    3. Return value — the type and what it contains
    4. Raises / throws — any exceptions or errors it can produce
    5. Edge cases — inputs or conditions that could cause unexpected behaviour
    6. Dependencies — which other functions or methods it calls
    7. Notable design decisions — anything worth flagging for documentation

    Also identify at the top level:
    - What problem this codebase solves overall
    - Any imported libraries or modules and what they are used for
    - Any global variables or constants and their purpose

    Format your output with clear headings and bullet points.
    Be precise, technical, and complete.
    Do not add filler or padding.
    Your output goes directly to a documentation writer agent —
    completeness and accuracy are critical.
    """,
    model=MODEL
)




# Section 3 — Agent 2: Documentation Writer
# 3 / 6
# Agent 2 — turns analysis into professional Markdown docs
# Agent
# The Documentation Writer receives the analyst's structured output and turns it into developer-ready Markdown. It never sees the raw code directly — only the analysis. This separation means each agent can be excellent at its specific job.

# The system prompt specifies the exact sections to produce, the format of each, and even the tone. The more specific the system prompt, the more consistent the output across different codebases.

# ── Agent 2: Documentation Writer ────────────────────────────────────────
#
# Job: receive structured analysis → write professional Markdown docs.
# Receives: the Code Analyst's output + the original code for reference.
# Produces: complete Markdown documentation ready for a README or wiki.
doc_writer = Agent(
    name="Documentation Writer",
    instructions="""
    You are a professional technical documentation writer.
    You will receive a structured analysis of Python or JavaScript code,
    along with the original code for reference.

    Produce complete, professional documentation in Markdown format.
    Your output must contain exactly these sections:

    ## Overview
    2-3 sentences. What this code does and what problem it solves.
    Written for a developer who has never seen this codebase before.

    ## Installation & Dependencies
    List any libraries or modules imported. Note if they need installing.

    ## API Reference
    For every function, method, and class:
    ### FunctionName / ClassName
    One-line description.
    **Parameters:**
    | Name | Type | Description |
    |------|------|-------------|
    | param | type | what it does |
    **Returns:** type — description
    **Raises:** ExceptionType — when it is raised (omit section if none)

    ## Usage Examples
    At least 2 complete, realistic, copy-pasteable code examples.
    Show the most common use cases. Include expected output as comments.

    ## Edge Cases & Gotchas
    Bullet list of important limitations, non-obvious behaviours,
    or things that could trip up a developer using this code.

    Write for a developer audience. Be precise and professional.
    Use proper Markdown throughout. Do not add extra commentary
    outside these sections.
    """,
    model=MODEL
)




# Section 4 — Agent 3: Quality Reviewer

# Agent 3 — reviews, corrects, and polishes the documentation

# The Quality Reviewer is the final gate. It receives both the generated documentation AND the original code, and it checks one against the other. Its job is to catch anything the writer got wrong, fix gaps, and polish the language. The user never sees the intermediate outputs — only what the Reviewer approves and returns.

# Having a dedicated review agent is what separates a production pipeline from a prototype. It catches errors the writer makes when the analysis was ambiguous or incomplete.

# ── Agent 3: Quality Reviewer ─────────────────────────────────────────────
#
# Job: review the documentation against the original code.
# Receives: generated documentation + original code.
# Produces: corrected, polished, publication-ready documentation.
#
# This agent sees BOTH the docs AND the original code — it can
# catch errors the writer made by cross-referencing them directly.
quality_reviewer = Agent(
    name="Quality Reviewer",
    instructions="""
    You are a senior technical documentation reviewer.
    You will receive generated documentation AND the original code it describes.

    Your job is to:

    1. VERIFY accuracy — check every parameter name, type, return value,
       and description against the actual code. Correct any errors.

    2. CHECK completeness — confirm every function, method, and class
       in the code is documented. Add anything missing.

    3. IMPROVE clarity — rewrite any explanations that are vague,
       confusing, or too technical without explanation.

    4. VALIDATE examples — check that the usage examples are correct
       and would actually run without errors.

    5. POLISH language — fix grammar, improve sentence flow, ensure
       consistent tone throughout.

    Return the complete, corrected documentation in full Markdown.
    Do not add commentary about what you changed — just return the
    final, polished documentation and nothing else.
    """,
    model=MODEL
)




# Section 5 — The Pipeline Function
# New concept: async def
# This function is defined with async def instead of just def. That makes it an asynchronous function — also called a coroutine. It can use await inside it, which means it can pause and wait for the AI to respond without blocking everything else. Gradio knows how to call async def functions automatically — this is one of the reasons we chose Gradio.

# run_pipeline() — the function Gradio will call

# This is the single function the Gradio UI imports and calls. It takes the user's code and language as inputs, runs all three agents in sequence, and returns the final documentation string. The handoff pattern from Notebook 03 is used here exactly as we practised it.

# The function signature uses type hints — code: str means the code parameter should be a string, and -> str means the function returns a string. Type hints don't change how the code runs — they make it easier to understand and catch bugs early.

async def run_pipeline(code: str, language: str) -> str:
    """
    Run the three-agent documentation pipeline.

    Takes raw source code and produces complete Markdown documentation.
    Called by the Gradio UI in app.py.

    Args:
        code:     The raw source code to document (Python or JavaScript).
        language: The programming language — 'Python' or 'JavaScript'.

    Returns:
        A string of complete, polished Markdown documentation.
    """

    # Guard: if the user submits empty code, return early with a message.
    # strip() removes leading/trailing whitespace before checking.
    if not code.strip():
        return "⚠️ No code was provided. Please paste or upload a file."

    # ── Step 1: Code Analyst ──────────────────────────────────────────────
    # We tell the analyst what language it's looking at so it applies
    # the right mental model (Python conventions vs JavaScript conventions).
    analysis_result = await Runner.run(
        code_analyst,
        f"""Analyse this {language} code thoroughly:

{code}"""
    )
    # Extract the plain text from the result object
    analysis = analysis_result.final_output

    # ── Step 2: Documentation Writer — HANDOFF ────────────────────────────
    # We pass BOTH the analyst's output AND the original code.
    # The writer uses the analysis as its primary source,
    # but can cross-reference the original code if needed.
    doc_result = await Runner.run(
        doc_writer,
        f"""Write complete professional documentation using this analysis:

--- ANALYSIS ---
{analysis}

--- ORIGINAL {language.upper()} CODE (for reference) ---
{code}"""
    )
    draft_docs = doc_result.final_output

    # ── Step 3: Quality Reviewer — FINAL HANDOFF ──────────────────────────
    # The reviewer sees the draft documentation AND the original code.
    # It can catch errors by comparing them directly.
    review_result = await Runner.run(
        quality_reviewer,
        f"""Review and polish this documentation against the original code.

--- DOCUMENTATION TO REVIEW ---
{draft_docs}

--- ORIGINAL {language.upper()} CODE ---
{code}"""
    )

    # Return the final polished documentation string
    return review_result.final_output




# Section 6 — The Streaming Function
# New concept: streaming with async def + yield
# Instead of waiting for all three agents to finish before showing anything, streaming lets us send partial updates to the UI as each agent completes. The user sees progress in real time rather than staring at a blank screen for 30 seconds. We do this with yield — a keyword that means "send this value now, then continue running." A function that uses yield is called a generator. An async function that uses yield is an async generator.

# stream_pipeline() — yields progress updates to the Gradio UI

# This function does the same work as run_pipeline() but yields intermediate status messages and partial results as each agent finishes. Gradio's streaming output component receives each yielded value and updates the UI immediately. This is what makes the app feel alive and responsive rather than frozen.

# The AsyncGenerator[str, None] return type hint means: "this function yields strings asynchronously and never returns a final value." The None is the send type — not important to understand right now.

async def stream_pipeline(
    code: str,
    language: str
) -> AsyncGenerator[str, None]:
    """
    Streaming version of run_pipeline().

    Yields progress updates after each agent completes so the
    Gradio UI can show the user what is happening in real time.

    Args:
        code:     The raw source code to document.
        language: 'Python' or 'JavaScript'.

    Yields:
        Strings — status messages and partial/final documentation.
    """

    # Guard: empty input check — same as run_pipeline()
    if not code.strip():
        yield "⚠️ No code was provided. Please paste or upload a file."
        return

    # yield sends a value to the UI immediately and then keeps running.
    # The Gradio component replaces its current content with each new value.
    yield "⏳ Step 1 of 3 — Code Analyst is reading your code..."

    # ── Step 1: Code Analyst ──────────────────────────────────────────────
    analysis_result = await Runner.run(
        code_analyst,
        f"Analyse this {language} code thoroughly:\n\n{code}"
    )
    analysis = analysis_result.final_output

    yield "⏳ Step 2 of 3 — Documentation Writer is drafting the docs..."

    # ── Step 2: Documentation Writer ──────────────────────────────────────
    doc_result = await Runner.run(
        doc_writer,
        f"""Write complete professional documentation using this analysis:

--- ANALYSIS ---
{analysis}

--- ORIGINAL {language.upper()} CODE (for reference) ---
{code}"""
    )
    draft_docs = doc_result.final_output

    yield "⏳ Step 3 of 3 — Quality Reviewer is checking and polishing..."

    # ── Step 3: Quality Reviewer ──────────────────────────────────────────
    review_result = await Runner.run(
        quality_reviewer,
        f"""Review and polish this documentation against the original code.

--- DOCUMENTATION TO REVIEW ---
{draft_docs}

--- ORIGINAL {language.upper()} CODE ---
{code}"""
    )

    # Final yield — the complete polished documentation.
    # This is the last value sent to the UI, replacing the status message.
    yield review_result.final_output