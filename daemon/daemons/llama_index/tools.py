from llama_index.core import Settings
from llama_index.core.tools import FunctionTool
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.agent import ReActAgent

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool

import time, re

#############################
# Non-interactive tools
#############################

def kali_rag_tool():
  # Load documents, create tools
  embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
  )

  Settings.embed_model = embed_model

  kali_docs = SimpleDirectoryReader(
      input_files=["./learningkalilinux.pdf"]
  ).load_data()

  print("indexing...")
  kali_index = VectorStoreIndex.from_documents(kali_docs)
  print("done...")

  kali_docs_tool = QueryEngineTool.from_defaults(
      kali_index.as_query_engine(),
      name="kali_manual",
      description="Query about the usage of Kali Linux. Use this tool if unsure of what to do next or how to perform an action.",
  )

  return kali_docs_tool



#############################
# Interactive tools
#############################

def sleep_tool(env, msf_env):
  def sleep(sleep_time: int = 5) -> str:
    """ Use this to sleep up to 10 seconds at a time while waiting on a command to finish executing. When this tool finishes, carefully read the output to decide whether to sleep again or proceed.
      Args:
        sleep_time (int): The number of seconds to sleep for while waiting for another command to finish execution.
    """
    tts = min(sleep_time, 10)
    sleep_intervals = tts // env.timeout
    term_feedback = ""
    msf_feedback = ""
    for t in range(0, sleep_intervals):
      time.sleep(env.timeout)
      term_feedback += env.step("", no_op=True)
      msf_feedback += msf_env.step("", no_op=True)
    
      
    return "## Terminal Window ##\n"+term_feedback+"\n## MSF Window ##\n"+msf_feedback

  return FunctionTool.from_defaults(sleep)


def kali_cmd_tool(env):
  def kali_terminal(command: str) -> str:
    """ Execute a single command inside a Kali Linux VM.

    Critical NOTES:
    - Do not use tools that require or launch a GUI.
    - Do not provide commands with placeholders such as <argument>.
    - Carefully examine the output in the Observation to look for errors and adjust accordingly.
    - Commands to avoid: vim, nano
    - Avoid lengthy bruteforcing attacks such as guessing SSH passwords with rockyou.txt

      Args:
        command (str): The terminal command to execute.
    """
    cmd_out = env.step(command)
    return "## Terminal Window ##\n" + cmd_out
  
  return FunctionTool.from_defaults(kali_terminal)

def _to_raw_string(s):
  return repr(s).strip("'")

import re

def _winpath_escaper(path):
    # Escape backslashes in the path
    path = path.replace("\\", "\\\\")

    path = re.sub(r'\\\\\\+', r'\\\\', path)
    
    # First regex pattern to capture the part within parentheses
    first_regex = re.compile(r'(\\(.*)\ ([^\\]*)\\)')
    # Second regex pattern to find within the captured part
    second_regex = re.compile(r'(\ )')
    # Replacement text for the second regex
    replacement_text = r'\ '
    
    # Find all matches for the first regex
    matches = list(first_regex.finditer(path))
    
    # Initialize an offset to adjust replacement positions
    offset = 0
    
    # Loop through each match
    for match in matches:
        captured_text = match.group(1)  # Get the captured part        
        # Apply the second regex to replace within the captured part
        modified_text = second_regex.sub(replacement_text, captured_text)
        # Calculate the start and end positions adjusted by the current offset
        start = match.start(1) + offset
        end = match.end(1) + offset
        # Replace the original captured portion with the modified text
        path = path[:start] + modified_text + path[end:]
        
        # Update the offset by the difference in lengths between modified and original texts
        offset += len(modified_text) - len(captured_text)
    
    return re.sub(r'\\+ ', r'\ ', path)

def metasploit_tool(env_msf, default_nic=None):
  env_msf.step("msfconsole -q")
  if default_nic:
    env_msf.step(f"setg LHOST {default_nic}")
  env_msf.step("")
  def msfconsole(command: str) -> str:
    """ Execute a SINGLE command inside the msfconsole. This tool facilitates finding and using exploits against targets. 
    Metasploit features modules for exploitation and privilege escalation against targets.
    
    NOTE: Once a target is successfully compromised, use this tool to interact with the target file system. Pay careful attention to the feedback given by exploits and commands. Some exploits may take a while to execute; if the msfconsole or meterpreter prompts do not appear in the output, try sleeping until the exploit finishes.

    Pay extreme attention to whether you are executing within msfconsole or meterpreter.
    For privilege escalation, be sure to configure the modules in msfconsole.
    
    Useful msfconsole commands:
    - 'search <target service> <version number>' --> look for Metasploit modules matching the target service; do NOT use CVE strings as arguments to this.
    - 'setg <param> <value>' --> set a global value once to save time; do this for things like rhosts or lhost values
    - 'searchsploit <target service> <version number>' --> alternative search method if the initial search returns no results
    - 'use </path/to/exploit>' --> select an exploit
    - 'show payloads' --> show payload options for selected exploit; only necessary if one is not selected by default.
    - 'set <parameter> <value>' --> configure options of the exploit
    - 'exploit' --> launch the exploit
    - 'sessions -i <session_number>' --> from msfconsole, select an open meterpreter session. If this errors, do NOT use '-i'
    - 'sessions -u -1' --> upgrade most recent session to meterpreter; use if the observation does not include 'meterpreter>'

    Useful meterpreter commands:
    - 'search -f <filename>' --> locate a file on the target machine
    - 'background' --> switch back to the msfconsole to configure an exploit.
    - 'sessions <session number>' --> Use this format when using the meterpreter prompt.
    - 'run post/multi/recon/local_exploit_suggester' --> a module to assist with privilege escalation

    Critical NOTE: NEVER USE <PLACEHOLDERS> when executing commands; use the actual values.

      Args:
        command (str): A SINGLE msfconsole command to execute - NEVER chain commands. Use actual values for arguments, do NOT provide commands with placeholders such as <argument>.
    """

    timeout = env_msf.timeout
    if command == "run" or command == "exploit":
      timeout *= 8
    if "search -f" in command:
      timeout *= 6

    cmd_out = env_msf.step(_winpath_escaper(_to_raw_string(command)), timeout=timeout)

    if "meterpreter" in cmd_out:
      cmd_out = _winpath_escaper(cmd_out)
    if "local_exploit_suggester" in cmd_out:
      cmd_out = cmd_out[cmd_out.find("Valid modules"):]

    if len(cmd_out) > 16384:
      cmd_out = cmd_out[:16384] + "\n## Message Truncated ##\n"

    return "## msfconsole Window ##\n" + cmd_out
  
  return FunctionTool.from_defaults(msfconsole)



def reset_connection_tool(env, msf_env):
  def reset_connection() -> str:
    """ Use this function to reset the connection to Kali/MSF environment if not receiving outputs from actions. Note that previous actions in msfconsole will be lost.
    """
    env.reset()
    msf_env.reset()
    msf_env.step("msfconsole -q")
    return "Connection Reset.\n"
  
  return FunctionTool.from_defaults(reset_connection)

def nmap_tool(env):
  def nmap(ip_addr_range: str = "", script="vuln") -> str:
    """ Perform an NMAP scan of the ip addr range, returning open ports and associated service versions. Use this tool only to perform scans. This tool will return a lot of information; focus on the running services, their versions, and any obvious vulnerabilities and exploits suggested.

      Args:
        ip_addr_range (str): IP address range to scan.
        script (str): The name of a NMAP Scripting Engine (NSE) script to use to gather service specific information.
    """
    command = f"nmap -sV --top-ports 3300 --min-rate=1000 --stats-every=3 -T5 --script={script} {ip_addr_range} --open"
    cmd_out = env.step(command, timeout=18)
    return "### Starting Scan: ###\n" + cmd_out[cmd_out.find("Nmap scan report"):]
  
  return FunctionTool.from_defaults(nmap)


def man_tool(env):
  def documentation_page(program_name: str) -> str:
    """ Read the manual page for a given command line tool to check options and usage.
      Args:
        program_name (str): name of Kali Linux program to view additional information for.
    """
    command = "man "+program_name+" | cat"
    cmd_out = env.step(command)
    return cmd_out
  
  return FunctionTool.from_defaults(documentation_page)

