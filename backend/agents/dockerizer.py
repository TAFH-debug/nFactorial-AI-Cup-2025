import json
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    convert_system_message_to_human=True,
    model_kwargs={"response_mime_type": "application/json"}
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
     You are a DevOps Engineer. 
     You will be provided with a project root directory files and folders.
     Your task is to write Dockerfile for the project.
     You must provide a Dockerfile code that can be run immediately. 
     Ensure that you know enough details about the project to be able to write the code.
     Be absolutely sure that the Dockerfile will work.
     Do not overcomplicate the Dockerfile.
     Make sure that every executed command will be found.
     See every config file to maximally fit the project.
     Do not include lines that are not needed for the Dockerfile to work.
     Do not include any other symbols in the output except the json object.
    To help you in this task you have access to the following tools:
    
    {{tools}}
    
    Use the following json format:
    
    {{
        "thought": "Think about what to do",
        "action": "tool_name",
        "action_input": "the input to the tool",
        "observation": "the result of the action",
        "dockerfile": "the Dockerfile code"
    }}
    """),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

def get_dockerfile_code_tool(dir_fn, cat_fn):

    def wrapper(comment: str):
        """
        Get the dockerfile code.
        Use this only if there is some error in the previous dockerfile code.
        comment: comment to be considered while writing the dockerfile.
        """
        return get_dockerfile_code(dir_fn, cat_fn, comment)
    
    return wrapper

async def get_dockerfile_code(dir_fn, cat_fn, comment: str=None):
    tools = [tool(dir_fn), tool(cat_fn)]

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(tools=tools, agent=agent, verbose=True)

    data = {
        "comment": comment,
        "files": dir_fn('.')
    }
    result = await agent_executor.ainvoke({"input": str(data)})

    if (result["output"].startswith("```")):
        result = result["output"].split("```json")[1]
        result = result.split("```")[0]
    else:
        result = result["output"]
    return json.loads(result)["dockerfile"]

