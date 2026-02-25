---
title: My Career
emoji: ":zap:"
colorFrom: pink
colorTo: yellow
sdk: gradio
sdk_version: 5.23.1
app_file: app.py
pinned: false
tags:
- smolagents
- agent
- smolagent
- tool
- agent-course
---

# My Career

A Gradio app that wraps a `smolagents` CodeAgent to answer questions about a resume and generate career-related outputs (summaries, leadership highlights, role fit), plus a few utility tools (currency conversion, time zones, webpage-to-markdown, and image generation).

**What This Project Does**
- Launches a chat UI for interacting with an LLM-backed agent.
- Preloads a resume into memory and provides predefined prompt buttons for common career tasks.
- Exposes tools for resume Q&A, webpage-to-markdown extraction, currency conversion, timezone lookup, text-to-image, and a superhero-themed party idea generator.

**How It Works**
- `app.py` builds a `CodeAgent` using `HfApiModel` (Qwen2.5-Coder-32B-Instruct) and a set of custom tools.
- The agent is wrapped in a small Gradio UI (`ResumeChatUI`) that supports chat and one-click predefined prompts.
- A resume text blob is embedded directly in `app.py` and is auto-loaded at startup.

**Project Structure**
- `app.py` Main entry point. Defines tools, loads prompts, builds the agent, and launches the Gradio UI.
- `Gradio_UI.py` Generic streaming Gradio UI helper for `smolagents` (not used by `app.py`, but available).
- `prompts.yaml` Prompt templates used by the agent.
- `agent.json` Serialized agent configuration (tools + model + prompt templates).
- `tools/` Custom tool implementations (final answer, web search, visit webpage, superhero theme).
- `requirements.txt` Base Python dependencies (see notes below for additional runtime packages).

**Setup**
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:
   - `pip install -r requirements.txt`
   - `pip install gradio beautifulsoup4 pytz pillow`
3. If the model is gated or rate-limited, set a Hugging Face token in your environment (for example `HF_TOKEN`).

**Run**
- `python app.py`

**Notes**
- The resume content is currently hardcoded in `app.py`. Replace the `resume_text` string with your own data.
- The `upload_resume` tool currently returns the hardcoded resume text rather than reading a file.
- `tools/visit_webpage.py` and `tools/web_search.py` exist for agent configs like `agent.json`, but they are not wired into `app.py`.
