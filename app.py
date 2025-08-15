from smolagents import CodeAgent, DuckDuckGoSearchTool, load_tool, tool
import datetime
import requests
import pytz
import yaml
import PyPDF2
from transformers import T5Tokenizer, T5ForConditionalGeneration
from tools.final_answer import FinalAnswerTool

# -------------------- Global Resume Storage -------------------- #
resume_text = ""

# -------------------- Load FLAN-T5-Small Model -------------------- #
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")

def generate_answer(prompt: str, max_length: int = 256) -> str:
    """Generate answer using FLAN-T5-Small"""
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=max_length)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# -------------------- Tools -------------------- #

@tool
def upload_resume(file_path: str) -> str:
    """Upload a resume (PDF or TXT) so the agent can answer questions about it."""
    global resume_text
    if file_path.lower().endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file_path)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text() + "\n"
            return "Resume uploaded successfully (PDF)."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    elif file_path.lower().endswith(".txt"):
        try:
            with open(file_path, "r") as f:
                resume_text = f.read()
            return "Resume uploaded successfully (TXT)."
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    else:
        return "Unsupported file type. Use PDF or TXT."

@tool
def ask_resume_question(question: str) -> str:
    """Ask a question about the uploaded resume."""
    global resume_text
    if not resume_text:
        return "No resume uploaded yet. Please upload your resume first."
    prompt = f"My resume is:\n{resume_text}\n\nQuestion: {question}\nAnswer concisely:"
    return generate_answer(prompt)

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert a given amount from one currency to another."""
    url = "https://api.exchangerate.host/convert"
    params = {"from": from_currency.upper(), "to": to_currency.upper(), "amount": amount}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("success"):
            return f"{amount} {from_currency} = {data['result']} {to_currency}"
        else:
            return f"Error fetching conversion rate: {data}"
    except Exception as e:
        return f"Error: {e}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Fetch the current local time in a specified timezone."""
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"Current time in {timezone}: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

@tool
def my_custom_tool(arg1: str, arg2: int) -> str:
    return "What magic will you build ?"

# -------------------- Agent Setup -------------------- #
final_answer = FinalAnswerTool()

# Load image generation tool (optional)
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=None,  # We use FLAN-T5 directly inside tools
    tools=[
        final_answer,
        DuckDuckGoSearchTool(),
        convert_currency,
        get_current_time_in_timezone,
        image_generation_tool,
        upload_resume,
        ask_resume_question,
        my_custom_tool
    ],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

# -------------------- Launch Chat Interface -------------------- #
# Optional: Keep Gradio UI for chat
from Gradio_UI import GradioUI
GradioUI(agent).launch()

# -------------------- Example Usage in Code -------------------- #
# Uncomment to test in code without UI
print(upload_resume("/Users/kani/Documents/resume.pdf"))
print(ask_resume_question("What programming languages do I know?"))
