import json
from langchain_core.tools import tool
import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from github_api import get_dir_files, get_file_content

os.environ["GOOGLE_API_KEY"] = "AIzaSyA0mMdZMZd-WNxfkvWhJtc-Oy_sxpD0wkY"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    convert_system_message_to_human=True,
)

@tool
def dir(path):
    """
    Get names of files and directories in a given path.
    """
    files = []
    for file in os.listdir(path):
        name = os.path.basename(file)
        if os.path.isfile(file):
            files.append({"name": name, "type": "file"})
        else:
            files.append({"name": name, "type": "directory"})
    return files

@tool
def cat(path):
    """
    Get the content of a file.
    """
    with open(path, "r") as f:
        return f.read()

prompt = ChatPromptTemplate.from_messages([
    ("system", """
     You are a DevOps Engineer. 
     You will be provided with a project root directory files and folders.
     Your task is to write Dockerfile for the project.
     You must provide a Dockerfile code that can be run immediately. 
     Ensure that you know enough details about the project to be able to write the code.
     Do not overcomplicate the Dockerfile, be sure that it will work.
     Do not include lines that are not needed for the Dockerfile to work.
     Your output must json object with the following keys:
     - dockerfile: the Dockerfile code
    To help you in this task you have access to the following tools:
    
    {{tools}}
    
    Use the following json format:
    
    {{
        "thought": "Think about what to do",
        "action": "tool_name",
        "action_input": "the input to the tool",
        "observation": "the result of the action",
        "final_answer": "the final answer to the original input question"
    }}
    """),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

def get_dockerfile_code(dir_fn, cat_fn):
    tools = [tool(dir_fn), tool(cat_fn)]

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(tools=tools, agent=agent, verbose=True)

    result = agent_executor.invoke({"input": str(dir_fn('.'))})
    result = result["output"].split("```json")[1].split("```")[0]
    return json.loads(result)['final_answer']["dockerfile"]

