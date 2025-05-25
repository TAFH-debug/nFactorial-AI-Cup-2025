import io
from langchain_google_genai import ChatGoogleGenerativeAI
import paramiko
import logging
from typing import Optional, List, Dict, Union
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool

from agents.dockerizer import get_dockerfile_code, get_dockerfile_code_tool
from agents.github_api import get_repo_read_functions
from agents.deployer import SSHDeployer


async def redeploy(github_repo: str, hostname: str, username: str, key: str, env_file: str, base_path: str, tracer = None):
    deployer = SSHDeployer(hostname=hostname, username=username)
    deployer.connect(key=key)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-05-20",
        convert_system_message_to_human=True,
        model_kwargs={"response_mime_type": "application/json"}
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a DevOps Engineer. 
        You will be provided with project repository link.
        Your task is to redeploy the project on the remote server.
        There may be an existing deployment on the server.
        Consider pulling the latest changes from the repository.
        Do not change Dockerfile if possible.
        You should stop the existing deployment then apply the changes to the project and then redeploy it.
        Also be careful when manipulating the docker containers.
        You will be provided by sudo password to run commands.
        After running docker container, ensure that the container is running and accessible from the outside using curl or check the logs.
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

    dir_fn, cat_fn = get_repo_read_functions(github_repo, base_path)
    tools = [tool(deployer.execute_command), tool(get_dockerfile_code_tool(dir_fn, cat_fn))]

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        tools=tools, 
        agent=agent, 
        verbose=True, 
        max_iterations=None
    )

    data = {
        "link": github_repo,
        "env_file": env_file,
        "base_path": base_path
    }

    result = agent_executor.invoke({"input": str(data)}, {
        "callbacks": [tracer] if tracer else None
    })

    return result["output"]

