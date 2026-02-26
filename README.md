# 📄 Codebase Documentation Generator

[![Live Demo](https://img.shields.io/badge/demo-Hugging%20Face%20Spaces-blue)](https://huggingface.co/spaces/Neolegend/codebase-doc-generator)
[![Python](https://img.shields.io/badge/python-3.13-green)]()
[![Framework](https://img.shields.io/badge/framework-Gradio-orange)]()
[![Agents](https://img.shields.io/badge/agents-openai--agents-purple)]()

An AI-powered tool that reads your Python or JavaScript codebase and generates
complete, professional documentation — including docstrings, API reference,
usage examples, parameter descriptions, return types, and edge cases.
Powered by a three-agent pipeline built with the OpenAI Agents SDK.

![Demo Screenshot](assets/demo(app_result).png)

## Features

- 🤖 **Three-agent pipeline** — Code Analyst → Documentation Writer → Quality Reviewer
- 📝 **Paste or upload** — paste code directly or upload a `.py` or `.js` file
- ⚡ **Streaming output** — see progress in real time as each agent completes
- 📥 **Download ready** — export finished documentation as a `.md` file
- 🐍 **Python & JavaScript** — handles both languages

## How It Works

The tool runs a sequential three-agent pipeline on your code:

1. **Code Analyst** — reads the raw code and extracts a structured analysis:
   functions, parameters, return types, dependencies, edge cases
2. **Documentation Writer** — takes the analysis and writes professional Markdown
   documentation with API reference, usage examples, and gotchas
3. **Quality Reviewer** — cross-references the documentation against the original
   code, corrects errors, fills gaps, and polishes the language

## Tech Stack

| Tool | Purpose |
|------|---------|
| `openai-agents` | Multi-agent orchestration |
| `gradio` | Web UI with streaming output |
| `openrouter` | LLM API (model-agnostic) |
| `python-dotenv` | Environment variable management |

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/codebase-doc-generator
cd codebase-doc-generator
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env
uv sync
uv run python app.py
```

## Sample Output

See [sample_output/sample_documentation.md](sample_output/sample_documentation.md)
for an example of the documentation this tool generates.

## Project Structure

```
codebase-doc-generator/
├── app.py                  # Gradio web interface
├── app/
│   └── agents.py           # Three-agent pipeline
├── notebooks/experiments/  # Learning notebooks (Phase 2)
├── assets/                 # Screenshots
├── sample_output/          # Example generated documentation
└── .env.example            # Environment variable template
```