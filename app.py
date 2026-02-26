# ================================================================
# app.py
# Gradio web interface for the Codebase Documentation Generator.
# Run with: uv run python app.py
# ================================================================

# gradio — the UI framework. Import as 'gr' — standard convention.
import gradio as gr

# pathlib.Path — creates file paths that work on Windows, Mac, Linux
from pathlib import Path

# datetime — generates timestamps for unique output filenames
from datetime import datetime

# stream_pipeline — our three-agent pipeline from Phase 3.
# app.agents means: go into app/, find agents.py, import from it.
from app.agents import stream_pipeline


# ── Helper: save docs to disk for download ────────────────────────────────

def save_documentation(content: str) -> str:
    """Save documentation string to a .md file. Returns the file path."""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = temp_dir / f"documentation_{timestamp}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return str(filepath)


# ── Main generate function — called by the Generate button ────────────────

async def generate(code_input: str, file_input, language: str):
    """
    Streams documentation to the UI as the agents work.
    Yields tuples of (output_text, download_path).
    """
    # If a file was uploaded, read it. Otherwise use pasted code.
    if file_input is not None:
        with open(file_input.name, "r", encoding="utf-8") as f:
            code = f.read()
    else:
        code = code_input

    # Guard: no code provided
    if not code.strip():
        yield ("⚠️ Please paste code or upload a file first.", None)
        return

    # Stream the pipeline — yield each chunk to the UI as it arrives
    final_output = ""
    async for chunk in stream_pipeline(code, language):
        final_output = chunk
        yield (chunk, None)

    # Pipeline done — save and offer the download
    if final_output.strip():
        download_path = save_documentation(final_output)
        yield (final_output, download_path)


# ── Gradio UI ─────────────────────────────────────────────────────────────

with gr.Blocks(title="Codebase Doc Generator") as demo:

    gr.Markdown("""
    # 📄 Codebase Documentation Generator
    Paste your Python or JavaScript code, or upload a file.
    Three AI agents will analyse it and generate complete professional documentation.
    """)

    with gr.Row():

        with gr.Column(scale=1):
            gr.Markdown("### Input")

            code_input = gr.Code(
                label="Paste your code here",
                language="python",
                lines=20
            )

            file_input = gr.File(
                label="Or upload a file (.py or .js)",
                file_types=[".py", ".js"]
            )

            language_input = gr.Dropdown(
                label="Language",
                choices=["Python", "JavaScript"],
                value="Python"
            )

            with gr.Row():
                generate_btn = gr.Button(
                    "Generate Documentation",
                    variant="primary"
                )
                clear_btn = gr.Button(
                    "Clear",
                    variant="secondary"
                )

        with gr.Column(scale=1):
            gr.Markdown("### Output")

            output = gr.Markdown(
                label="Generated Documentation",
            )

            download_output = gr.File(
                label="Download as .md file",
                interactive=False
            )

    generate_btn.click(
        fn=generate,
        inputs=[code_input, file_input, language_input],
        outputs=[output, download_output]
    )

    clear_btn.click(
        fn=lambda: (None, None, None, None, "Python"),
        inputs=[],
        outputs=[code_input, file_input, output, download_output, language_input]
    )


# ── Launch ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo.launch(inbrowser=True)