import io
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import paramiko
import logging
from typing import Optional, List, Dict, Union
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool

from dockerizer import get_dockerfile_code
from github_api import get_repo_read_functions

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


key = """
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEAsLUHrNvQMiKGLFXw+iSO1TSfRB7pMv5x8CocxIbQ3wgjlEIgWbb1
+ZyypKsYKi4jA6b9dqdK/qY2S9BB7EJ7M+K1f59tbayth9rkidUovHriaVPuoBmSBcjQrA
GCKoSVY7cYyxLbAvuIxY4HDSSjsUSA96Y7rmoin5ZIWwohXKSEIzECnXne10oti1Mbk4KM
URt8fcK/J8NWB58oGiMNmSa96P/CHWSEIjJhlRWl78QAoja/8UTkmqNvwILyFTECzXEtuM
GujITcmMox2P3jEVXcZ+SPtzQL6T/YJyHY+aurq31yFeJOVfWqxU2XrvX3r1jMytMrdy2t
tYUg89CmyzyCbRira1Ls1q3HrHLqV+959h7Znp7X38DexvJd6AsJbjEftIzoFSPHOR0QDd
tmOPFIx7kol6BsHPhdYGJs7MqIeZ93Rg2UiYRBVbyph058wvosKZhlMZNjjMRM3l2vbWaK
Yl3jlRtvDbsDOAulbUgGmwdZrffhJbaK1GGR+g89AAAFiGAm7CZgJuwmAAAAB3NzaC1yc2
EAAAGBALC1B6zb0DIihixV8PokjtU0n0Qe6TL+cfAqHMSG0N8II5RCIFm29fmcsqSrGCou
IwOm/XanSv6mNkvQQexCezPitX+fbW2srYfa5InVKLx64mlT7qAZkgXI0KwBgiqElWO3GM
sS2wL7iMWOBw0ko7FEgPemO65qIp+WSFsKIVykhCMxAp153tdKLYtTG5OCjFEbfH3CvyfD
VgefKBojDZkmvej/wh1khCIyYZUVpe/EAKI2v/FE5Jqjb8CC8hUxAs1xLbjBroyE3JjKMd
j94xFV3Gfkj7c0C+k/2Cch2Pmrq6t9chXiTlX1qsVNl671969YzMrTK3ctrbWFIPPQpss8
gm0Yq2tS7Natx6xy6lfvefYe2Z6e19/A3sbyXegLCW4xH7SM6BUjxzkdEA3bZjjxSMe5KJ
egbBz4XWBibOzKiHmfd0YNlImEQVW8qYdOfML6LCmYZTGTY4zETN5dr21mimJd45Ubbw27
AzgLpW1IBpsHWa334SW2itRhkfoPPQAAAAMBAAEAAAGABoXqjnlxsROHMCrxJjrIrwjAZ8
uAUuFxbL01zvCTr+XAlw3JSoH4rSWG/GzmMC4kr1MdyaCHD8TjRszmlqoAdpcomX3oJqgq
xy89kWGRePlw5V2hZHWa51t5stRi2roYza8cNsQK/x55raJsbjbGwVCgNii6qCLnvAL87I
Lb8CLaBnaLsysSsP3ecWWB2z1yoE65BMLkFrvT+MDpwjU+e/prJScz2RrHhVsUMRtr53L2
ICtrzjaya2b3ILMroyoOqJEiJxKnvI4sqLNd8o91z9GZ5O0ry2N77mxeFeBmiShP5DsTs0
eABwotE1K2fV6J5RKCGKDKp9xr1C0NSNb3USnAEL+iFweCsQZXhn/6+xaRBeDaAnGifHAZ
qHV5oBp9pHJjJ9Xwmnk9Cpp7M22ooTePq/wJ7TDi+yaaF2CSMS/ekw/ZKFVTKxXiDBoimi
5nUMCe1n+X5lmwDDnPT6wD5BajTVQRdmtxXDb1glEyd67XA4yBldbEeMp6WMA15YR9AAAA
wEhTPbpsJfC8wh13pxgjbrJP2HcwXNRx4GPMxbyceSnPpKjan5n/tE7yEUdtgJH09XfD7O
th4F7Lj3PCd6IzKgNSTnB+1oxwysbVnzdE0KzD3PcOScCugRPaqSiDZBD3BKIzuNHJEsaR
Swyw1qyt7vrBsCey5fMhWz0XBVjz4NTTgpr32hW/dR23Y3Uqw4TTnwF32iAHXm89mz/vrG
AkhrZbhfEdXuOTZKnFrt8ECbo1Edlfv96ABdxn+GA/bQW7HAAAAMEA3gqBHCZuutQW2qd5
cz9bDNh3qFc0TJ0HXj43/jk9G3jhQcfWaVi/ZVj39Olicyg/DcB5/E18FYiWwID2DWHBYt
hOEnzXKCVfr6UUeZ7I0cbZsI1wBJ5219gw8NXGDOW9NdYALul0TQTW+kTZnLecwVz8DZJ0
cCl+xn3sGJrD0smQXY9P4t6Cyn/c5nMb60qFmEAVYnAuhlVgT5NBBC//DZ6ZJ7m3hPFSGG
eVome9AwT9uZDe+/3mYZn2TtxVGL6jAAAAwQDLu5VyRR6tIgDkZJ7jZVWHWyePkKq8Cf28
NaYHikhpF0Xy8QIz2vGrfhM8STq+E12j3X6R7nlFO4xKIq9F0qJWNtC6W+sEtoW76gAZMq
JyTEoe0oBdvSmuZtzKN0e8uABPoeVYQ24s0HV8KaqnKpVT8b9QWa+3Pk/wh9NIneid80S+
OEAJ3oFPCvv3HwA8S+IXyuWLsCFcRXQIhnV3atJMzI6RAjwYeToA2zg9LbvZTmd8GJ7/wn
A9HENljOD4OJ8AAAANYXVzaGFobWFuMjAwNwECAwQFBg==
-----END OPENSSH PRIVATE KEY-----
"""



def deploy(github_repo: str, hostname: str, username: str, key: str, env_file: str):
    deployer = SSHDeployer(hostname=hostname, username=username)
    deployer.connect(key=key)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-05-20",
        convert_system_message_to_human=True,
        response_format={"type": "json_object"}
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

    tools = [tool(deployer.execute_command), tool(get_dockerfile_code)]

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(tools=tools, agent=agent, verbose=True)

    data = {
        "link": github_repo,
        "dockerfile": get_dockerfile_code(get_repo_read_functions(github_repo)),
        "env_file": env_file
    }
    result = agent_executor.invoke({"input": str(data)})

    return result["output"]

print(deploy(github_repo="https://github.com/TAFH-debug/nextjs_template", hostname="35.188.179.99", username="aushahman2007", key=key, env_file="DATABASE_URL=postgresql://neondb_owner:npg_Y7arHl4cWzRb@ep-damp-silence-a8bvmqvq-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"))
