import os
from typing import Optional
from smolagents import ToolCallingAgent, HfApiModel, tool
import PyPDF2

# ---------------- Global Resume Storage ----------------
RESUME_TEXT: Optional[str] = None

# ---------------- Tool Definitions ----------------

@tool
def upload_resume(file_path: str) -> str:
    """
    Upload a resume from a local PDF file path.
    Args:
        file_path: Path to the resume PDF (e.g., '~/Documents/resume.pdf')
    Returns:
        Success or failure message.
    """
    global RESUME_TEXT
    try:
        with open(os.path.expanduser(file_path), "rb") as f:
            reader = PyPDF2.PdfReader(f)
            RESUME_TEXT = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return f"✅ Resume loaded from {file_path}"
    except Exception as e:
        return f"❌ Failed to load resume: {str(e)}"


@tool
def summarize_resume() -> str:
    """
    Summarize the contents of the uploaded resume.
    Returns:
        A short summary or an error message if no resume is loaded.
    """
    global RESUME_TEXT
    if not RESUME_TEXT:
        return "❌ No resume uploaded yet."
    return f"📄 Resume Summary (truncated):\n{RESUME_TEXT[:500]}..."


@tool
def query_resume(question: str) -> str:
    """
    Answer questions about the uploaded resume.
    Args:
        question: The question to ask about the resume.
    Returns:
        An answer from the resume, or a message if the info is not found.
    """
    global RESUME_TEXT
    if not RESUME_TEXT:
        return "❌ No resume uploaded yet."
    
    # simple keyword search (can improve with LLM if needed)
    if question.lower() in RESUME_TEXT.lower():
        return f"✅ Found relevant info for: '{question}'"
    return f"ℹ️ Could not find direct answer for: '{question}'"


# ---------------- Agent Setup ----------------
model = HfApiModel(model="mistralai/Mistral-7B-Instruct-v0.3")  # Model supporting chat completion

agent = ToolCallingAgent(
    tools=[upload_resume, summarize_resume, query_resume],
    model=model,
    max_steps=5,
)

# ---------------- Auto Resume Load ----------------
RESUME_PATH = "/Users/kani/Documents/resume.pdf"
if os.path.exists(os.path.expanduser(RESUME_PATH)):
    print("📂 Auto-loading resume...")
    print(upload_resume(RESUME_PATH))
else:
    print("⚠️ No resume found at ~/Documents/resume.pdf")


# ---------------- Example Usage ----------------
if __name__ == "__main__":
    print(agent.run("Summarize my resume"))
    print(agent.run("What programming languages do I know?"))
