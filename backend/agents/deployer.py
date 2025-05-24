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

class SSHDeployer:
    def __init__(self, hostname: str, username: str, 
                 key_filename: Optional[str] = None, port: int = 22):
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename
        self.port = port
        self.client: Optional[paramiko.SSHClient] = None
        self.logger = logging.getLogger(__name__)

    def connect(self, key: str) -> bool:
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                "hostname": self.hostname,
                "username": self.username,
                "port": self.port,
                "pkey": paramiko.RSAKey.from_private_key(io.StringIO(key))
            }
            
            if self.key_filename:
                connect_kwargs["key_filename"] = self.key_filename

            self.client.connect(**connect_kwargs)
            self.logger.info(f"Successfully connected to {self.hostname}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.hostname}: {str(e)}")
            return False

    def execute_command(self, command: str, timeout: int = 60) -> Dict[str, Union[int, str, str]]:
        """
        Execute a command on the remote server.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dict containing:
                - exit_code: Command exit code
                - stdout: Command standard output
                - stderr: Command standard error
        """
        if not self.client:
            raise RuntimeError("Not connected to remote server. Call connect() first.")
            
        try:
            self.logger.debug(f"Executing command: {command}")
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout, get_pty=True)
            
            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode().strip()
            stderr_str = stderr.read().decode().strip()
            
            if exit_code != 0:
                self.logger.warning(f"Command failed with exit code {exit_code}")
                self.logger.warning(f"stderr: {stderr_str}")
            else:
                self.logger.debug("Command executed successfully")
                
            return {
                "exit_code": exit_code,
                "stdout": stdout_str,
                "stderr": stderr_str
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute command: {str(e)}")
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }

    def execute_commands(self, commands: List[str], timeout: int = 60) -> List[Dict[str, Union[int, str, str]]]:
        """
        Execute multiple commands sequentially.
        
        Args:
            commands: List of commands to execute
            timeout: Timeout for each command in seconds
            
        Returns:
            List of command execution results
        """
        return [self.execute_command(cmd, timeout) for cmd in commands]

    def close(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.logger.info(f"Closed connection to {self.hostname}")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()



def deploy(github_repo: str, hostname: str, username: str, key: str, env_file: str, tracer = None):
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
        You will be provided with project repository link and dockerfile code.
        Your task is to deploy the project on the remote server.
        You will be provided by sudo password to run commands.
        After running docker container, ensure that the container is running and accessible from the outside.
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

    dir_fn, cat_fn = get_repo_read_functions(github_repo)
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
        max_iterations=1
    )

    data = {
        "link": github_repo,
        "dockerfile": get_dockerfile_code(dir_fn, cat_fn),
        "env_file": env_file
    }

    result = agent_executor.invoke({"input": str(data)}, {
        "callbacks": [tracer] if tracer else None
    })

    return result["output"]

