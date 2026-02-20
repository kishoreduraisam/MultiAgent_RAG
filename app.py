from smolagents import CodeAgent, HfApiModel, load_tool, tool
from tools.final_answer import FinalAnswerTool
from tools.superhero_party_theme_generator import SuperheroPartyThemeTool as SuperheroPartyThemeGenerator
import datetime
import requests
import pytz
import yaml
import PyPDF2
import os
import gradio as gr
from Gradio_UI import GradioUI
from bs4 import BeautifulSoup
from markdownify import markdownify as md


# ------------------- Webpage Tool ------------------- #
@tool
def webpage_to_markdown(url: str) -> str:
    """
    Fetches a webpage and returns its content in markdown format.
    Useful for reading and analyzing web content like job postings or company information.
    
    Args:
        url: The URL of the webpage to fetch
        
    Returns:
        The webpage content in markdown format
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.decompose()
        
        markdown_content = md(str(soup), heading_style="ATX")
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in markdown_content.split('\n')]
        cleaned_markdown = '\n'.join(line for line in lines if line)
        
        return cleaned_markdown
        
    except requests.RequestException as e:
        return f"Error fetching webpage: {str(e)}"
    except Exception as e:
        return f"Error processing webpage: {str(e)}"

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
    params = {"from": from_currency.upper(), "to": to_currency.upper(), "amount": amount,"access_key": "a31468775105e25711ddd2fd1ab039db"}
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

image_generation_tool = load_tool("m-ric/text-to-image", trust_remote_code=True)
superhero_party_theme_generator = SuperheroPartyThemeGenerator()

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[
        final_answer,
        convert_currency,
        get_current_time_in_timezone,
        image_generation_tool,
        upload_resume,
        ask_resume_question,
        webpage_to_markdown,  # ← NEW TOOL ADDED
        superhero_party_theme_generator
    ],
    max_steps=6,
    verbosity_level=1,
    prompt_templates=prompt_templates
)

# Auto-load resume on startup
upload_resume()

# ------------------- Gradio UI with Predefined Prompts ------------------- #
class ResumeChatUI:
    def __init__(self, agent):
        self.agent = agent

    def launch(self):
        with gr.Blocks() as demo:
            chatbot = gr.Chatbot(type="messages")

            # Send function
            def run_agent(user_input, history):
                history = history or []
            
                reply = self.agent.run(user_input)
                # Debug: print agent attributes
                print("Agent attributes:", dir(self.agent))
                print("Reply type:", type(reply))
                print("Reply:", reply)
            
                history.append({"role": "user", "content": user_input})
            
                from PIL import Image as PILImage
                from PIL import PngImagePlugin
                
                def add(content):
                    history.append({"role": "assistant", "content": content})
            
                # Handle AgentImage type (smolagents wrapper)
                if hasattr(reply, '__class__') and 'AgentImage' in reply.__class__.__name__:
                    # AgentImage contains a file path - use it directly
                    image_path = str(reply)
                    # For Gradio Chatbot with type="messages", we need to use a dict format
                    add({"path": image_path})
                
                elif isinstance(reply, list):
                    for item in reply:
                        if isinstance(item, tuple):
                            item = item[1]
            
                        if hasattr(item, '__class__') and 'AgentImage' in item.__class__.__name__:
                            add({"path": str(item)})
                        elif isinstance(item, (PILImage.Image, PngImagePlugin.PngImageFile)):
                            # Save temp file and use path
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
                                item.save(f.name)
                                add({"path": f.name})
                        else:
                            add(str(item))
            
                else:
                    if isinstance(reply, (PILImage.Image, PngImagePlugin.PngImageFile)):
                        # Save temp file and use path
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
                            reply.save(f.name)
                            add({"path": f.name})
                    else:
                        add(str(reply))
            
                return history, ""



            send = gr.Button("Send")
            send.click(run_agent, [msg, chatbot], [chatbot, msg])

        demo.launch()

# ------------------- Launch ------------------- #
ResumeChatUI(agent).launch()
