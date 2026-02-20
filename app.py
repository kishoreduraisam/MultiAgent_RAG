from smolagents import CodeAgent, HfApiModel, load_tool, tool,GoogleSearchTool, VisitWebpageTool
from smolagents.utils import encode_image_base64, make_image_url
from smolagents import OpenAIServerModel
from tools.final_answer import FinalAnswerTool
from tools.superhero_party_theme_generator import SuperheroPartyThemeTool as SuperheroPartyThemeGenerator
from typing import Optional, Tuple
import datetime
import requests
import pytz
import yaml
import PyPDF2
import os
import gradio as gr
import math
from Gradio_UI import GradioUI
from PIL import Image


# ------------------- Other Tools ------------------- #
@tool
def calculate_cargo_travel_time(
    origin_coords: Tuple[float, float],
    destination_coords: Tuple[float, float],
    cruising_speed_kmh: Optional[float] = 750.0,  # Average speed for cargo planes
) -> float:
    """
    Calculate the travel time for a cargo plane between two points on Earth using great-circle distance.

    Args:
        origin_coords: Tuple of (latitude, longitude) for the starting point
        destination_coords: Tuple of (latitude, longitude) for the destination
        cruising_speed_kmh: Optional cruising speed in km/h (defaults to 750 km/h for typical cargo planes)

    Returns:
        float: The estimated travel time in hours

    Example:
        >>> # Chicago (41.8781° N, 87.6298° W) to Sydney (33.8688° S, 151.2093° E)
        >>> result = calculate_cargo_travel_time((41.8781, -87.6298), (-33.8688, 151.2093))
    """

    def to_radians(degrees: float) -> float:
        return degrees * (math.pi / 180)

    # Extract coordinates
    lat1, lon1 = map(to_radians, origin_coords)
    lat2, lon2 = map(to_radians, destination_coords)

    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0

    # Calculate great-circle distance using the haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    distance = EARTH_RADIUS_KM * c

    # Add 10% to account for non-direct routes and air traffic controls
    actual_distance = distance * 1.1

    # Calculate flight time
    # Add 1 hour for takeoff and landing procedures
    flight_time = (actual_distance / cruising_speed_kmh) + 1.0

    # Format the results
    return round(flight_time, 2)


print(calculate_cargo_travel_time((41.8781, -87.6298), (-33.8688, 151.2093)))

def check_reasoning_and_plot(final_answer, agent_memory):
    multimodal_model = OpenAIServerModel("gpt-4o", max_tokens=8096)
    filepath = "saved_map.png"
    assert os.path.exists(filepath), "Make sure to save the plot under saved_map.png!"
    image = Image.open(filepath)
    prompt = (
        f"Here is a user-given task and the agent steps: {agent_memory.get_succinct_steps()}. Now here is the plot that was made."
        "Please check that the reasoning process and plot are correct: do they correctly answer the given task?"
        "First list reasons why yes/no, then write your final decision: PASS in caps lock if it is satisfactory, FAIL if it is not."
        "Don't be harsh: if the plot mostly solves the task, it should pass."
        "To pass, a plot should be made using px.scatter_map and not any other method (scatter_map looks nicer)."
    )
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": make_image_url(encode_image_base64(image))},
                },
            ],
        }
    ]
    output = multimodal_model(messages).content
    print("Feedback: ", output)
    if "FAIL" in output:
        raise Exception(output)
    return True


# ------------------- Agent Setup ------------------- #
final_answer = FinalAnswerTool()
model = HfApiModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.getenv("HF_TOKEN")  # Optional, for private models or higher rate limits
)


image_generation_tool = load_tool("m-ric/text-to-image", trust_remote_code=True)
superhero_party_theme_generator = SuperheroPartyThemeGenerator()


web_agent = CodeAgent(
    model=model,
    tools=[
        final_answer,
        image_generation_tool,
        superhero_party_theme_generator,
        calculate_cargo_travel_time,
        GoogleSearchTool("serper"), 
        VisitWebpageTool()
    ],
    max_steps=20,
    verbosity_level=1,
    planning_interval=4,
    additional_authorized_imports=["pandas"],
    name="web_agent",
    description="Browses the web to find information"
)

manager_agent = CodeAgent(
    model=InferenceClientModel("deepseek-ai/DeepSeek-R1", provider="together", max_tokens=8096),
    tools=[calculate_cargo_travel_time],
    managed_agents=[web_agent],
    additional_authorized_imports=[
        "geopandas",
        "plotly",
        "shapely",
        "json",
        "pandas",
        "numpy",
    ],
    planning_interval=5,
    verbosity_level=2,
    final_answer_checks=[check_reasoning_and_plot],
    max_steps=15
)

manager_agent.visualize()


# ------------------- Gradio UI with Predefined Prompts ------------------- #
class ResumeChatUI:
    def __init__(self, agent):
        self.agent = agent

    def launch(self):
        with gr.Blocks() as demo:
            chatbot = gr.Chatbot(type="messages")
            msg = gr.Textbox()

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
ResumeChatUI(manager_agent).launch()
