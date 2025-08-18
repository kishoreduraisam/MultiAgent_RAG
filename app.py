import os
import json
from typing import Optional
from smolagents import tool, ToolCallingAgent, HfApiModel
from PyPDF2 import PdfReader

# Global storage for the resume text (survives across tool calls)
RESUME_STORE: dict[str, str] = {}


@tool
def upload_resume(file_path: str) -> str:
    """
    Upload and parse a resume from a local PDF file.

    Args:
        file_path (str): Path to the resume PDF (e.g., '~/Documents/resume.pdf').

    Returns:
        str: Confirmation message once the resume is uploaded.
    """
    expanded_path = os.path.expanduser(file_path)
    if not os.path.exists(expanded_path):
        return f"Error: File not found at {expanded_path}"

    reader = PdfReader(expanded_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    RESUME_STORE["resume_text"] = text
    return "Resume uploaded successfully."


@tool
def summarize_resume() -> str:
    """
    Summarize the uploaded resume.

    Returns:
        str: A summary of the resume content.
    """
    resume_text = RESUME_STORE.get("resume_text")
    if not resume_text:
        return "No resume uploaded. Please use upload_resume first."

    # Here we just do a naive summary (first 500 chars).
    # In practice, you could run this through a model for better summarization.
    summary = resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
    return f"Resume Summary:\n{summary}"


@tool
def query_resume(question: str) -> str:
    """
    Query details from the uploaded resume.

    Args:
        question (str): A natural language question about the resume.

    Returns:
        str: An answer based on the resume content.
    """
    resume_text = RESUME_STORE.get("resume_text")
    if not resume_text:
        return "No resume uploaded. Please use upload_resume first."

    # Naive keyword match (replace with RAG or model query if needed)
    if question.lower() in resume_text.lower():
        return f"Yes, the resume mentions: {question}"
    return f"Could not find information about: {question}"


# ---------------- Agent Setup ----------------

# Use a model that supports chat completions
model = HfApiModel(model="mistralai/Mistral-7B-Instruct-v0.3")  

agent = ToolCallingAgent(
    tools=[upload_resume, summarize_resume, query_resume],
    model=model,
    max_steps=5,
    verbosity=2,
)


if __name__ == "__main__":
    # Example usage
    print(agent.run("Please load my resume from ~/Documents/resume.pdf"))
    print(agent.run("Summarize my resume"))
    print(agent.run("Does my resume mention Python?"))
