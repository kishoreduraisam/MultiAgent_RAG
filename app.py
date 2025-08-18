from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
import datetime
import requests
import pytz
import yaml
import os
import PyPDF2
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI

# --- Global variable to store resume text ---
resume_text = ""

# --- Tools ---

@tool
def my_custom_tool(arg1: str, arg2: int) -> str:
    """
    Example custom tool placeholder.

    Args:
        arg1 (str): The first argument.
        arg2 (int): The second argument.

    Returns:
        str: A placeholder response message.
    """
    return "What magic will you build?"

@tool
def upload_resume(file_path: str = None) -> str:
    """
    Upload a resume (PDF or TXT) so the agent can answer questions about it.
    If no file path is provided, it defaults to '~/Documents/resume.pdf'.

    Args:
        file_path (str, optional): Path to the resume file. Defaults to None.

    Returns:
        str: Success or error message after attempting to read the file.
    """
    global resume_text
    # Use default path if not provided
    if file_path is None:
        file_path = os.path.expanduser("~/Documents/resume.pdf")

    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    if file_path.lower().endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file_path)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text() + "\n"
            return f"Resume uploaded successfully (PDF): {file_path}"
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    elif file_path.lower().endswith(".txt"):
        try:
            with open(file_path, "r") as f:
                resume_text = f.read()
            return f"Resume uploaded successfully (TXT): {file_path}"
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    else:
        return "Unsupported file type. Use PDF or TXT."

@tool
def ask_resume_question(question: str) -> str:
    """
    Ask a question about the uploaded resume. The agent uses the content of the resume
    to generate a concise answer.

    Args:
        question (str): The question you want to ask about your resume.

    Returns:
        str: The agent's answer based on the resume content.
    """
    global resume_text
    if not resume_text:
        return "No resume uploaded yet. Please upload your resume first."

    prompt = f"My resume is:\n{resume_text}\n\nQuestion: {question}\nAnswer concisely:"
    response = model.generate(prompt)
    return response

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert a given amount from one currency to another using exchangerate.host API.

    Args:
        amount (float): The amount to convert.
        from_currency (str): Currency code to convert from (e.g., 'USD').
        to_currency (str): Currency code to convert to (e.g., 'EUR').

    Returns:
        str: Conversion result or error message.
    """
    url = "https://api.exchangerate.host/convert"
    params = {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if "result" in data:
            return f"{amount} {from_currency} = {data['result']} {to_currency}"
        else:
            return f"Error fetching conversion: {data}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """
    Fetch the current local time in a specified timezone.

    Args:
        timezone (str): A valid timezone string (e.g., 'America/New_York').

    Returns:
        str: The current local time in the given timezone or an error message.
    """
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time: {str(e)}"

# --- Initialize agent ---

final_answer = FinalAnswerTool()

model = HfApiModel(
    model_id="google/flan-t5-small",
    temperature=0.5,
    max_tokens=512
)

image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as f:
    prompt_templates = yaml.safe_load(f)

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
    name="ResumeAgent",
    description="Agent that can answer questions about your resume",
    prompt_templates=prompt_templates
)

# --- Launch Gradio ---
GradioUI(agent).launch()
