---
title: Multi Agent RAG
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

# Multi Agent RAG

A Gradio app that demonstrates a **multi-agent** setup using `smolagents`: a manager agent delegates web research to a web agent and can return either text answers or map visualizations (Plotly). It also includes a sample geospatial utility tool for cargo-flight travel time calculations.

**What This Project Does**
- Runs a **manager agent** with a delegated **web agent** for search + webpage browsing.
- Supports answering prompts in chat and optionally returning a Plotly map in the UI.
- Provides a sample tool (`calculate_cargo_travel_time`) that computes great-circle flight time between coordinates.

**How It Works**
- `web_agent` uses `GoogleSearchTool("serper")` and `VisitWebpageTool()` to browse the web and gather info.
- `manager_agent` can call `web_agent`, run geospatial/plotting code, and return a Plotly figure.
- The Gradio UI renders chat responses and shows a map if the agent returns a `plotly.graph_objects.Figure`.

**Project Structure**
- `app.py` Main entry point. Defines agents, tools, and the Gradio UI, then launches the app.
- `Gradio_UI.py` Generic streaming UI for `smolagents` (not used by `app.py`, but available).
- `prompts.yaml` Prompt templates used by the agent(s).
- `agent.json` Serialized agent configuration (tools + model + prompt templates).
- `tools/` Custom tool implementations (final answer, web search, visit webpage, superhero theme).
- `requirements.txt` Python dependencies for web search, plotting, geo tooling, and Gradio.

**Setup**
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:
   - `pip install -r requirements.txt`
3. If the model is gated or rate-limited, set a Hugging Face token (e.g., `HF_TOKEN`).

**Run**
- `python app.py`

**Example Prompts**
- `Find the top 5 busiest container ports in the world and plot them on a world map.`
- `Compare average cargo flight time from Chicago to Sydney vs. Chicago to Tokyo.`
- `Find recent news about [topic] and summarize it in 5 bullets.`

**Notes**
- `app.py` currently prints a sample `calculate_cargo_travel_time` result at startup.
- The `check_reasoning_and_plot` hook is defined but commented out.
- `tools/web_search.py` exists but the app uses `GoogleSearchTool("serper")` directly instead.
