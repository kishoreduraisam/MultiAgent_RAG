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



# ------------------- Other Tools ------------------- #


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
        image_generation_tool,
        superhero_party_theme_generator
    ],
    max_steps=6,
    verbosity_level=1,
    prompt_templates=prompt_templates
)


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
