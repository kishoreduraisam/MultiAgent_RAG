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

# Global variable to store resume text
resume_text = "KISHOREKUMAR DURAISAMYGreensboro, NC - 27455 • (646) 203-9531 • kishoreduraisamy@gmail.comCAREER PROFILETechnology Leader with over 18 years of experience leading globally distributed engineering teams, buildingInformation Technology solutions for medium to large size companies in various industries like e-commerce andfinancial sectors. Built and modernized high scale, low latency, resilient distributed systems that powered theplatforms in 8 countries and 5 languages. Proven experience in crafting and executing high level plans, as well asdriving architectural designs and actual implementations, using agile methodologies.Core Competencies include Enterprise Architecture, Digital Transformation, Data Engineering, Data Analysis,Personalization & Recommendation Engines, Global Delivery, Cloud Engineering, Microservices,Containerization, Enterprise Observability, Continuous Integration and Continuous Deployment, EmployeeCareerDevelopment, Vendor Management. Certified Scrum Master Jun 2016 and PMI - Agile Certified PractitionerACP.CAREER HIGHLIGHTS• Increased the revenue by $500,000 annually by building the Data Pipeline and Data Engineering infrastructureto collect the customer behavior data to enable to build a more personalized shopping experience to thecustomers.• Increased the systems uptime from 99.4% to 99.9% by building a robust enterprise observability platformthereby reducing the customer impacting incidents and improving the shopping experience of the customers.• Increased the frequency of feature releases to the customers from twice a week to multiple times a day bydefining the process for automating the CI/CD processes to enable to push out the features faster.PROFESSIONAL EXPERIENCEMARKET AMERICA - SHOP.COM Greensboro, NC 2016 - PresentMarket America – SHOP.COM is a Product Brokerage and Internet Marketing Company that specializes in Oneto-One Marketing and Social Shopping system for entrepreneurs to create a significant ongoing income, whileproviding consumers a better way to shop. Served as a key senior engineering leader who led the strategy toidentify technological solutions to help the entrepreneurs grow their business.Director of Engineering, 2022- PresentServing as the Head of the Engineering team responsible for building Enterprise APIs and Systemsobservability platform that powers 9 e-commerce applications in 8 countries and 3 languages. Staff include 3Engineering Managers and 30 Software Engineers.• Lead Strategy, Best Practices, Design, Architecture, Integration, Resiliency for Enterprise API development.• Increased the systems uptime from 99.4% to 99.9% by building a robust enterprise observability platformthereby reducing the customer impacting incidents and improving the shopping experience of the customers.• Technical Program Manager & Product Owner for Enterprise API Development and Management.Engineering Manager, 2016- 2021Leading the API Development and Data Engineering teams that powered SHOP.COM website andpersonalized shopping experience for the customers. Staff included 15 Software Engineers distributed globally inthe USA, Australia and China.• Increased the revenue by $500,000 annually by building the infrastructure to collect the customer behaviordata to enable to analyze the customer shopper experience to build a more personalized shopping experienceto the customers.• Consolidated and centralized the API development process to define a centralized way to expose the data andbusiness logic that supports 9 e-commerce applications thereby reducing the footprint and enabling easy onboardingfor the clients.• Broke down the monolithic legacy applications and moved the core pieces of the application business logicinto micro services to reap the benefits of ease of scaling, deployment, resiliency and replaceability.!KISHOREKUMAR DURAISAMYGreensboro, NC - 27455 • (646) 203-9531 • kishoreduraisamy@gmail.comSYMBIO(formerly Freeborders, Inc.) San Jose, CA 2010-2015Symbio is a global digital services and consulting company that helps companies build innovative softwareproducts and transformative digital services that connect, engage and amaze their customers. Served as the OnsiteClient Manager for multiple customers helping to build IT Solutions by working with the offshore developmentteam based out of China.Software Development Manager, Monterey, CA, 2012-2015Served as the Onsite Client Manager for an e-commerce customer, SHOP.COM, who focused on buildingMarketplace Platform to onboard various merchants to have more offerings on their e-commerce Platform.Services included building a new Marketplace Admin Platform, Content Management Tool and various sitefeatures.• Reduced the on-boarding time of merchants to marketplace from several days to a couple of hours bybuilding a simple self-service Marketplace Platform for the merchants to onboard and start selling onSHOP.COM in no time• Increased the brand and deal awareness by building a content management tool that made it easy for themarketing teams to run and pre-scheduled various marketing campaigns and ads.• Grew the Symbio offshore team from 5 engineers to 15 engineers in the space of 3 years and helped tomodernize the architecture by moving some of the core features of the sites into micro-services basedarchitecture.Lead Consultant, Cincinnati, OH, 2010-2011Served as the Onsite Client Manager for a Financial customer, US Bank in the Treasury Management ITSolutions division. As part of US Bank’s engagement with Symbio, I lead a team of 20 engineers based out ofChina to help build their Treasury Management Solutions.• Increased the speed to market of receivables and payments feature by helping to spec out the requirementsand design and translate that to the offshore development team and ensure successful, high quality and ontimedelivery of the projects.• Grew the Symbio offshore team from 5 engineers to 20 engineers in the space of 4 years by building the trustwith the client and ensuring high quality deliverables.Additional Experience 2004-2010Advanced through various levels of Software Engineering Positions at the following workplaces• Dell(Formerly PerotSystems Inc,), Bengaluru, India 2004 - 2007• Oracle India Pvt. Limited in India, Bengaluru, India 2007-2008• Zenith Technologies Inc in FloridaDuring this time, I worked in the offshore Delivery model both as the offshore engineer as well as Onsite Engineerworking directly at the Customer site and gained valuable experience building IT solutions for HealthCare, Retailand Financial Industries.EDUCATIONBHARATHIAR UNIVERSITY, Coimbatore, Tamil Nadu, India, 2000-2004Bachelors in Engineering., Information Technology;SKILLSManagement, Highly-Scaled Distributed Systems, System Architecture, Software Design, SOA, REST APIs,Microservices, ETL, Data Engineering, E-commerce, Web Applications, Web Services, Project Management, AgileMethodologies, Java, XML, Java Enterprise Edition, Openshift, Kafka, ELK Stack, AWS Glue, AWS Athena,Presto, AWS Quicksights, Couchbase, SQLServer, Oracle DB, AWS Aurora"

# ----- Predefined prompts -----
predefined_prompts = [
    "Summarize my resume",
    "List the leadership skills in my resume",
    "Rewrite my resume as a senior engineering manager with impact-driven bullets",
    "Create an elevator pitch based on my resume",
    "What jobs am I best suited for based on my resume?",
]

# ------------------- Resume Tools ------------------- #
@tool
def upload_resume() -> str:
    """
    Upload a resume (PDF or TXT) so the agent can answer questions about it.
    Defaults to the user's resume at /Users/kani/Documents/resume.pdf.
    
        
    Returns:
        Confirmation message about upload status
    """
    global resume_text
    resume_text = "KISHOREKUMAR DURAISAMYGreensboro, NC - 27455 • (646) 203-9531 • kishoreduraisamy@gmail.comCAREER PROFILETechnology Leader with over 18 years of experience leading globally distributed engineering teams, buildingInformation Technology solutions for medium to large size companies in various industries like e-commerce andfinancial sectors. Built and modernized high scale, low latency, resilient distributed systems that powered theplatforms in 8 countries and 5 languages. Proven experience in crafting and executing high level plans, as well asdriving architectural designs and actual implementations, using agile methodologies.Core Competencies include Enterprise Architecture, Digital Transformation, Data Engineering, Data Analysis,Personalization & Recommendation Engines, Global Delivery, Cloud Engineering, Microservices,Containerization, Enterprise Observability, Continuous Integration and Continuous Deployment, EmployeeCareerDevelopment, Vendor Management. Certified Scrum Master Jun 2016 and PMI - Agile Certified PractitionerACP.CAREER HIGHLIGHTS• Increased the revenue by $500,000 annually by building the Data Pipeline and Data Engineering infrastructureto collect the customer behavior data to enable to build a more personalized shopping experience to thecustomers.• Increased the systems uptime from 99.4% to 99.9% by building a robust enterprise observability platformthereby reducing the customer impacting incidents and improving the shopping experience of the customers.• Increased the frequency of feature releases to the customers from twice a week to multiple times a day bydefining the process for automating the CI/CD processes to enable to push out the features faster.PROFESSIONAL EXPERIENCEMARKET AMERICA - SHOP.COM Greensboro, NC 2016 - PresentMarket America – SHOP.COM is a Product Brokerage and Internet Marketing Company that specializes in Oneto-One Marketing and Social Shopping system for entrepreneurs to create a significant ongoing income, whileproviding consumers a better way to shop. Served as a key senior engineering leader who led the strategy toidentify technological solutions to help the entrepreneurs grow their business.Director of Engineering, 2022- PresentServing as the Head of the Engineering team responsible for building Enterprise APIs and Systemsobservability platform that powers 9 e-commerce applications in 8 countries and 3 languages. Staff include 3Engineering Managers and 30 Software Engineers.• Lead Strategy, Best Practices, Design, Architecture, Integration, Resiliency for Enterprise API development.• Increased the systems uptime from 99.4% to 99.9% by building a robust enterprise observability platformthereby reducing the customer impacting incidents and improving the shopping experience of the customers.• Technical Program Manager & Product Owner for Enterprise API Development and Management.Engineering Manager, 2016- 2021Leading the API Development and Data Engineering teams that powered SHOP.COM website andpersonalized shopping experience for the customers. Staff included 15 Software Engineers distributed globally inthe USA, Australia and China.• Increased the revenue by $500,000 annually by building the infrastructure to collect the customer behaviordata to enable to analyze the customer shopper experience to build a more personalized shopping experienceto the customers.• Consolidated and centralized the API development process to define a centralized way to expose the data andbusiness logic that supports 9 e-commerce applications thereby reducing the footprint and enabling easy onboardingfor the clients.• Broke down the monolithic legacy applications and moved the core pieces of the application business logicinto micro services to reap the benefits of ease of scaling, deployment, resiliency and replaceability.!KISHOREKUMAR DURAISAMYGreensboro, NC - 27455 • (646) 203-9531 • kishoreduraisamy@gmail.comSYMBIO(formerly Freeborders, Inc.) San Jose, CA 2010-2015Symbio is a global digital services and consulting company that helps companies build innovative softwareproducts and transformative digital services that connect, engage and amaze their customers. Served as the OnsiteClient Manager for multiple customers helping to build IT Solutions by working with the offshore developmentteam based out of China.Software Development Manager, Monterey, CA, 2012-2015Served as the Onsite Client Manager for an e-commerce customer, SHOP.COM, who focused on buildingMarketplace Platform to onboard various merchants to have more offerings on their e-commerce Platform.Services included building a new Marketplace Admin Platform, Content Management Tool and various sitefeatures.• Reduced the on-boarding time of merchants to marketplace from several days to a couple of hours bybuilding a simple self-service Marketplace Platform for the merchants to onboard and start selling onSHOP.COM in no time• Increased the brand and deal awareness by building a content management tool that made it easy for themarketing teams to run and pre-scheduled various marketing campaigns and ads.• Grew the Symbio offshore team from 5 engineers to 15 engineers in the space of 3 years and helped tomodernize the architecture by moving some of the core features of the sites into micro-services basedarchitecture.Lead Consultant, Cincinnati, OH, 2010-2011Served as the Onsite Client Manager for a Financial customer, US Bank in the Treasury Management ITSolutions division. As part of US Bank’s engagement with Symbio, I lead a team of 20 engineers based out ofChina to help build their Treasury Management Solutions.• Increased the speed to market of receivables and payments feature by helping to spec out the requirementsand design and translate that to the offshore development team and ensure successful, high quality and ontimedelivery of the projects.• Grew the Symbio offshore team from 5 engineers to 20 engineers in the space of 4 years by building the trustwith the client and ensuring high quality deliverables.Additional Experience 2004-2010Advanced through various levels of Software Engineering Positions at the following workplaces• Dell(Formerly PerotSystems Inc,), Bengaluru, India 2004 - 2007• Oracle India Pvt. Limited in India, Bengaluru, India 2007-2008• Zenith Technologies Inc in FloridaDuring this time, I worked in the offshore Delivery model both as the offshore engineer as well as Onsite Engineerworking directly at the Customer site and gained valuable experience building IT solutions for HealthCare, Retailand Financial Industries.EDUCATIONBHARATHIAR UNIVERSITY, Coimbatore, Tamil Nadu, India, 2000-2004Bachelors in Engineering., Information Technology;SKILLSManagement, Highly-Scaled Distributed Systems, System Architecture, Software Design, SOA, REST APIs,Microservices, ETL, Data Engineering, E-commerce, Web Applications, Web Services, Project Management, AgileMethodologies, Java, XML, Java Enterprise Edition, Openshift, Kafka, ELK Stack, AWS Glue, AWS Athena,Presto, AWS Quicksights, Couchbase, SQLServer, Oracle DB, AWS Aurora"
    return resume_text

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

image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)
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
            msg = gr.Textbox(placeholder="Ask me anything about your resume...")

            # Predefined prompts
            predefined_prompts = [
                "Summarize my resume",
                "List my leadership achievements",
                "Rewrite my resume into bullet points with measurable impact",
                "Generate an elevator pitch based on my resume",
                "What job roles am I most suitable for given my experience?",
            ]

            # Send function
            def run_agent(user_input, history):
                history = history or []
            
                reply = self.agent.run(user_input)

                # Debug: print agent attributes
                print("Agent attributes:", dir(self.agent))
                print("Reply type:", type(reply))
                print("Reply:", reply)
            
                history.append({"role": "user", "content": user_input})
            
                from PIL.Image import Image
                from PIL import PngImagePlugin
            
                def add(content):
                    history.append({"role": "assistant", "content": content})
            
                # Try to capture images from agent's step outputs
                generated_images = []
                
                # Check agent's step_log attribute
                if hasattr(self.agent, 'step_log') and self.agent.step_log:
                    for step in self.agent.step_log:
                        if 'output' in step and isinstance(step['output'], (Image, PngImagePlugin.PngImageFile)):
                            img = step['output']
                            if img.mode != 'RGB':
                                img = img.convert("RGB")
                            generated_images.append(img)
                
                # Add captured images
                for img in generated_images:
                    add(img)
            
                # Process final reply
                if isinstance(reply, list):
                    for item in reply:
                        if isinstance(item, tuple):
                            item = item[1]
                        if isinstance(item, (Image, PngImagePlugin.PngImageFile)):
                            if item.mode != 'RGB':
                                item = item.convert("RGB")
                            add(item)
                        else:
                            add(str(item))
                else:
                    if isinstance(reply, (Image, PngImagePlugin.PngImageFile)):
                        if reply.mode != 'RGB':
                            reply = reply.convert("RGB")
                        add(reply)
                    else:
                        add(str(reply))
            
                return history, ""



            send = gr.Button("Send")
            send.click(run_agent, [msg, chatbot], [chatbot, msg])

            # Predefined prompt buttons (auto-send)
            with gr.Row():
                for p in predefined_prompts:
                    gr.Button(p).click(
                        run_agent,
                        inputs=[gr.State(value=p), chatbot],
                        outputs=[chatbot, msg]
                    )

        demo.launch()

# ------------------- Launch ------------------- #
ResumeChatUI(agent).launch()
