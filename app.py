from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
import datetime
import requests
import pytz
import yaml
import os
import PyPDF2
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI

# Path to store the resume persistently
RESUME_STORAGE_PATH = os.path.expanduser("~/Documents/resume_text.txt")

# ----------------------
# Tools
# ----------------------

@tool
def my_custom_tool(arg1: str, arg2: int) -> str:
    """A tool that does nothing yet"""
    return "What magic will you build?"

@tool
def upload_resume(file_path: str) -> str:
    """
    Upload a resume (PDF or TXT) so the agent can answer questions about it.
    The resume is stored persistently in RESUME_STORAGE_PATH.
    """
    file_path = os.path.expanduser(file_path)
    resume_text = ""

    if not os.path.exists(file_path):
        return f"File does not exist: {file_path}"

    try:
        if file_path.lower().endswith(".pdf"):
            reader = PyPDF2.PdfReader(file_path)
            for page in reader.pages:
                resume_text += page.extract_text() + "\n"
        elif file_path.lower().endswith(".txt"):
            with open(file_path, "r") as f:
                resume_text = f.read()
        else:
            return "Unsupported file type. Use PDF or TXT."

        # Save persistently
        with open(RESUME_STORAGE_PATH, "w") as f:
            f.write(resume_text)

        return f"Resume uploaded successfully from {file_path}."

    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def ask_resume_question(question: str) -> str:
    """
    Ask a question about the uploaded resume.
    """
    if not os.path.exists(RESUME_STORAGE_PATH):
        return "No resume uploaded yet. Please upload your resume first."

    with open(RESUME_STORAGE_PATH, "r") as f:
        resume_text = f.read()

    prompt = f"My resume is:\n{resume_text}\n\nQuestion: {question}\nAnswer concisely:"

    # Use the agent's model to generate answer
    response = model.generate(prompt)  # Adjust if your agent uses a different API
    return response

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    url = "https://api.exchangerate.host/convert"
    params = {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("success"):
            return f"The amount of {amount} {from_currency} in {to_currency} is: {data['result']}"
        else:
            return f"Error fetching conversion rate: {data}"
    except Exception as e:
        return f"Error: {e}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

# ----------------------
# Model and agent setup
# ----------------------

final_answer = FinalAnswerTool()

model = HfApiModel(
    max_tokens=1024,
    temperature=0.5,
    model_id="google/flan-t5-small",  # Free tier-friendly model
    custom_role_conversions=None,
)

# Optional: image generation tool
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[
        final_answer,
        DuckDuckGoSearchTool(),
        convert_currency,
        get_current_time_in_timezone,
        image_generation_tool,
        upload_resume,
        ask_resume_question
    ],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

# ----------------------
# Launch Gradio UI
# ----------------------
GradioUI(agent).launch()
