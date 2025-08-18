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
resume_text = "KISHOREKUMAR DURAISAMYGreensboro, NC - 27455 • (646) 203-9531 • kishoreduraisamy@gmail.comCAREER PROFILETechnology Leader with over 18 years of experience leading globally distributed engineering teams, buildingInformation Technology solutions for medium to large size companies in various industries like e-commerce andfinancial sectors. Built and modernized high scale, low latency, resilient distributed systems that powered theplatforms in 8 countries and 5 languages. Proven experience in crafting and executing high level plans, as well asdriving architectural designs and actual implementations, using agile methodologies.Core Competencies include Enterprise Architecture, Digital Transformation, Data Engineering, Data Analysis,Personalization & Recommendation Engines, Global Delivery, Cloud Engineering, Microservices,Containerization, Enterprise Observability, Continuous Integration and Continuous Deployment, EmployeeCareerDevelopment, Vendor Management. Certified Scrum Master Jun 2016 and PMI - Agile Certified PractitionerACP.CAREER HIGHLIGHTS• Increased the revenue by $500,000 annually by building the Data Pipeline and Data Engineering infrastructureto collect the customer behavior data to enable to build a more personalized shopping experience to thecustomers.• Increased the systems uptime from 99.4% to 99.9% by building a robust enterprise observability platformthereby reducing the customer impacting incidents and improving the shopping experience of the customers.• Increased the frequency of feature releases to the customers from twice a week to multiple times a day bydefining the process for automating the CI/CD processes to enable to push out the features faster.PROFESSIONAL EXPERIENCEMARKET AMERICA - SHOP.COM Greensboro, NC 2016 - PresentMarket America – SHOP.COM is a Product Brokerage and Internet Marketing Company that specializes in Oneto-One Marketing and Social Shopping system for entrepreneurs to create a significant ongoing income, whileproviding consumers a better way to shop. Served as a key senior engineering leader who led the strategy toidentify technological solutions to help the entrepreneurs grow their business.Director of Engineering, 2022- PresentServing as the Head of the Engineering team responsible for building Enterprise APIs and Systemsobservability platform that powers 9 e-commerce applications in 8 countries and 3 languages. Staff include 3Engineering Managers and 30 Software Engineers.• Lead Strategy, Best Practices, Design, Architecture, Integration, Resiliency for Enterprise API development.• Increased the systems uptime from 99.4% to 99.9% by building a robust enterprise observability platformthereby reducing the customer impacting incidents and improving the shopping experience of the customers.• Technical Program Manager & Product Owner for Enterprise API Development and Management.Engineering Manager, 2016- 2021Leading the API Development and Data Engineering teams that powered SHOP.COM website andpersonalized shopping experience for the customers. Staff included 15 Software Engineers distributed globally inthe USA, Australia and China.• Increased the revenue by $500,000 annually by building the infrastructure to collect the customer behaviordata to enable to analyze the customer shopper experience to build a more personalized shopping experienceto the customers.• Consolidated and centralized the API development process to define a centralized way to expose the data andbusiness logic that supports 9 e-commerce applications thereby reducing the footprint and enabling easy onboardingfor the clients.• Broke down the monolithic legacy applications and moved the core pieces of the application business logicinto micro services to reap the benefits of ease of scaling, deployment, resiliency and replaceability.!KISHOREKUMAR DURAISAMYGreensboro, NC - 27455 • (646) 203-9531 • kishoreduraisamy@gmail.comSYMBIO(formerly Freeborders, Inc.) San Jose, CA 2010-2015Symbio is a global digital services and consulting company that helps companies build innovative softwareproducts and transformative digital services that connect, engage and amaze their customers. Served as the OnsiteClient Manager for multiple customers helping to build IT Solutions by working with the offshore developmentteam based out of China.Software Development Manager, Monterey, CA, 2012-2015Served as the Onsite Client Manager for an e-commerce customer, SHOP.COM, who focused on buildingMarketplace Platform to onboard various merchants to have more offerings on their e-commerce Platform.Services included building a new Marketplace Admin Platform, Content Management Tool and various sitefeatures.• Reduced the on-boarding time of merchants to marketplace from several days to a couple of hours bybuilding a simple self-service Marketplace Platform for the merchants to onboard and start selling onSHOP.COM in no time• Increased the brand and deal awareness by building a content management tool that made it easy for themarketing teams to run and pre-scheduled various marketing campaigns and ads.• Grew the Symbio offshore team from 5 engineers to 15 engineers in the space of 3 years and helped tomodernize the architecture by moving some of the core features of the sites into micro-services basedarchitecture.Lead Consultant, Cincinnati, OH, 2010-2011Served as the Onsite Client Manager for a Financial customer, US Bank in the Treasury Management ITSolutions division. As part of US Bank’s engagement with Symbio, I lead a team of 20 engineers based out ofChina to help build their Treasury Management Solutions.• Increased the speed to market of receivables and payments feature by helping to spec out the requirementsand design and translate that to the offshore development team and ensure successful, high quality and ontimedelivery of the projects.• Grew the Symbio offshore team from 5 engineers to 20 engineers in the space of 4 years by building the trustwith the client and ensuring high quality deliverables.Additional Experience 2004-2010Advanced through various levels of Software Engineering Positions at the following workplaces• Dell(Formerly PerotSystems Inc,), Bengaluru, India 2004 - 2007• Oracle India Pvt. Limited in India, Bengaluru, India 2007-2008• Zenith Technologies Inc in FloridaDuring this time, I worked in the offshore Delivery model both as the offshore engineer as well as Onsite Engineerworking directly at the Customer site and gained valuable experience building IT solutions for HealthCare, Retailand Financial Industries.EDUCATIONBHARATHIAR UNIVERSITY, Coimbatore, Tamil Nadu, India, 2000-2004Bachelors in Engineering., Information Technology;SKILLSManagement, Highly-Scaled Distributed Systems, System Architecture, Software Design, SOA, REST APIs,Microservices, ETL, Data Engineering, E-commerce, Web Applications, Web Services, Project Management, AgileMethodologies, Java, XML, Java Enterprise Edition, Openshift, Kafka, ELK Stack, AWS Glue, AWS Athena,Presto, AWS Quicksights, Couchbase, SQLServer, Oracle DB, AWS Aurora"

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
