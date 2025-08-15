from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
import PyPDF2
import gradio as gr
from tools.final_answer import FinalAnswerTool


from Gradio_UI import GradioUI

# Global variable to store the resume text
resume_text = ""

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def my_custom_tool(arg1:str, arg2:int)-> str: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that does nothing yet 
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return "What magic will you build ?"

@tool
def upload_resume(file_path: str) -> str:
    """
    Upload a resume (PDF or TXT) so the agent can answer questions about it.
    Args:
        file_path: Path to the resume file to be reviewed
    """
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
    """
    Ask a question about the uploaded resume.
    Args:
        question: The question you want to ask
    """
    global resume_text
    if not resume_text:
        return "No resume uploaded yet. Please upload your resume first."
    
    # Combine resume and question for the agent
    prompt = f"My resume is:\n{resume_text}\n\nQuestion: {question}\nAnswer concisely:"
    
    # Generate the answer using your agent's model
    response = model.complete(prompt)  # Adjust this if your agent uses a different API
    return response


@tool
def convert_currency(amount:float, from_currency:str, to_currency:str)-> str:
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that converts a given amount from one currency to the other
    Args:
        amount: The Amount to convert
        from_currency: From currency
        to_currency: To Currency
    """
    url = f"https://api.exchangerate.host/convert"
    params = {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount,
        "access_key": "a31468775105e25711ddd2fd1ab039db"    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("success"):
            return f"The amount of {amount} {from_currency} in {to_currency} is : {data['result']}"

        else:
            print("Error fetching conversion rate:", data)
            return None
    except Exception as e:
        print("Error:", e)
        return None

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


final_answer = FinalAnswerTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='google/flan-t5-small',# it is possible that this model may be overloaded
custom_role_conversions=None,
)


# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer,DuckDuckGoSearchTool(), convert_currency,get_current_time_in_timezone,image_generation_tool,
        upload_resume,
        ask_resume_question], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

# -------------------- Launch Chat Interface -------------------- #
GradioUI(agent).launch()

# -------------------- Example Usage in Code -------------------- #
# Uncomment to test in code without the UI
upload_resume("~/Documents/resume.pdf")
print(ask_resume_question("What programming languages do I know?"))