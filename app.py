from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
from tools.final_answer import FinalAnswerTool
import datetime
import requests
import pytz
import yaml
import PyPDF2
import os
from Gradio_UI import GradioUI

# Global variable to store resume text
resume_text = ""

# ------------------- Resume Tools ------------------- #
@tool
def upload_resume(file_path: str = "/Users/kani/Documents/resume.pdf") -> str:
    """
    Upload a resume (PDF or TXT) so the agent can answer questions about it.
    Defaults to the user's resume at /Users/kani/Documents/resume.pdf.
    
    Args:
        file_path: Absolute path to the resume file (PDF or TXT)
        
    Returns:
        Confirmation message about upload status
    """
    global resume_text
    file_path = os.path.expanduser(file_path)

    if file_path.lower().endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file_path)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text() + "\n"
            return f"Resume uploaded successfully from {file_path}."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    elif file_path.lower().endswith(".txt"):
        try:
            with open(file_path, "r") as f:
                resume_text = f.read()
            return f"Resume uploaded successfully from {file_path}."
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    else:
        return "Unsupported file type. Use PDF or TXT."

@tool
def ask_resume_question(question: str) -> str:
    """
    Ask a question about the uploaded resume.
    
    Args:
        question: The question you want to ask
        
    Returns:
        Model-generated answer based on the resume text
    """
    global resume_text
    if not resume_text:
        upload_msg = upload_resume()
        if "successfully" not in upload_msg:
            return f"Could not load resume automatically: {upload_msg}"

    prompt = f"My resume is:\n{resume_text}\n\nQuestion: {question}\nAnswer concisely:"
    response = model.generate(prompt)
    return response

# ------------------- Other Tools ------------------- #
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert a given amount from one currency to another.
    
    Args:
        amount: The amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        
    Returns:
        Converted amount as a string
    """
    url = f"https://api.exchangerate.host/convert"
    params = {"from": from_currency.upper(), "to": to_currency.upper(), "amount": amount}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("success"):
            return f"{amount} {from_currency} = {data['result']} {to_currency}"
        else:
            return "Error fetching conversion rate."
    except Exception as e:
        return f"Error: {e}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """
    Fetch the current local time in a specified timezone.
    
    Args:
        timezone: Valid timezone string (e.g., 'America/New_York')
        
    Returns:
        Current time as string
    """
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"Current time in {timezone}: {local_time}"
    except Exception as e:
        return f"Error: {e}"

# ------------------- Agent Setup ------------------- #
final_answer = FinalAnswerTool()
model = HfApiModel(
    max_tokens=2096,
    temperature=0.5,
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',  # keep your current model
)

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
    prompt_templates=prompt_templates
)

# Auto-load resume on startup
upload_resume()

GradioUI(agent).launch()
