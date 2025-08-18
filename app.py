import os
from pathlib import Path
from smolagents import Tool, CodeAgent, HfApiModel
import PyPDF2

# Global variable to store resume text
RESUME_TEXT = ""


class UploadResumeTool(Tool):
    """
    Tool to upload and parse a resume from a local PDF file.

    Inputs:
        file_path (str): Path to the PDF resume file.
    
    Output:
        str: Success message after loading and parsing the resume.
    """

    name = "upload_resume"
    description = "Upload and parse a resume from a PDF file."

    def forward(self, file_path: str) -> str:
        global RESUME_TEXT
        file_path = os.path.expanduser(file_path)

        if not Path(file_path).exists():
            return f"Error: File not found at {file_path}"

        text = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())

        RESUME_TEXT = "\n".join(text)
        return f"Resume successfully loaded from {file_path}"


class SummarizeResumeTool(Tool):
    """
    Tool to summarize the uploaded resume.

    Inputs:
        None (uses the global resume text).
    
    Output:
        str: Short summary of the resume text.
    """

    name = "summarize_resume"
    description = "Summarize the uploaded resume."

    def forward(self) -> str:
        global RESUME_TEXT
        if not RESUME_TEXT:
            return "No resume has been uploaded yet."
        return f"Resume Summary:\n{RESUME_TEXT[:500]}..."  # preview only


class QueryResumeTool(Tool):
    """
    Tool to answer questions about the uploaded resume.

    Inputs:
        query (str): A question about the resume content.
    
    Output:
        str: Answer based on the uploaded resume text.
    """

    name = "query_resume"
    description = "Answer questions about the uploaded resume."

    def forward(self, query: str) -> str:
        global RESUME_TEXT
        if not RESUME_TEXT:
            return "No resume has been uploaded yet."
        return f"Answering based on resume: {query}\nRelevant content: {RESUME_TEXT[:500]}..."


# ---- Initialize Model ----
# Using a chat-compatible model (not flan-t5-small, which caused StopIteration)
model = HfApiModel("HuggingFaceH4/zephyr-7b-beta")

# ---- Initialize Agent ----
agent = CodeAgent(
    tools=[UploadResumeTool(), SummarizeResumeTool(), QueryResumeTool()],
    model=model,
    add_base_tools=True,
    max_iterations=5,
)

# ---- Automatically upload resume at startup ----
default_resume_path = "~/Documents/resume.pdf"
upload_tool = UploadResumeTool()
print(upload_tool.forward(default_resume_path))  # auto-load resume

# ---- Example Agent Chat ----
agent.run("Summarize my resume in 3 bullet points.")
