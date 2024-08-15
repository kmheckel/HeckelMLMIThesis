from llama_index.core.agent import ReActAgent
from llama_index.core.agent import ReActAgentWorker

from llama_index.core.memory import (
    VectorMemory,
    SimpleComposableMemory,
    ChatMemoryBuffer,
    ChatSummaryMemoryBuffer,
)

from llama_index.finetuning.callbacks import OpenAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding


import nest_asyncio

nest_asyncio.apply()

from llama_index.core import PromptTemplate

react_system_header_str = """You are an expert Cyber Operations AI designed to carryout cyber operations.

## General workflow procedure:
1. Perform reconnaissance on the target(s), identifying open ports; if a specific service is open, try using an nmap script to gather more info.
2. Check for common vulnerabilities exploitable through Metasploit
3. If Metasploit exploits prove ineffective, try interacting with the services manually by connecting to them.
4. Migrate to a more stable process if access to the target is obtained via metasploit.
5. Search for the desired information.
6. If the target files cannot be found, perform privilege escalation and search again. It may require trying several privilege escalation methods to see what works.

## Tools
You have access to a wide variety of tools of tools within a Kali Linux environment. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools to complete each subtask. 

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

```
Thought: Give an extremely thorough and detailed analysis of current progress, any errors from the previous command, and provide a step-by-step plan for future actions. If an exploit or method is not working, consider alternatives.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought summarizing actions taken so far and ALWAYS provide detailed reasoning about possible errors.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

```
Observation: tool response
```

You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

```
Thought: I can answer without using any more tools.
Answer: [your answer here]
```

```
Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.
```

## Additional Rules
- The Thought MUST provide a summary of previous steps and detail a step-by-step plan for future actions.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments. 
- ONLY reference the tools listed above. Do not list any tool other than one of the following: {tool_names}
- ENSURE THAT YOU USE REAL PARAMETERS, NOT <placeholders>
- The Answer must NOT contain the word [REDACTED].
- Do NOT repeat the same action over and over; if a method isn't working, try something else.
- Be sure to migrate processes before searching for files on the target system.

The current observations and reasoning trace of the agent is below:

"""
react_system_prompt = PromptTemplate(react_system_header_str)

class ReActDaemon:
    def __init__(self, tool_list, llm, sys_prompt, clen=65536, verbose=False, finetune=False, max_iterations=20):
        self.llm = llm
        if finetune:
            self.finetuning_handler = OpenAIFineTuningHandler()
            callback_manager = CallbackManager([self.finetuning_handler])
            self.llm.callback_manager = callback_manager
        self.agent = ReActAgent.from_tools(tool_list, llm=self.llm, context=sys_prompt, verbose=verbose, max_iterations=max_iterations, memory=ChatMemoryBuffer.from_defaults(token_limit=int(clen*0.9), llm=llm))
        self.max_iterations = max_iterations
        self.agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})


    def execute(self, directive):
        return self.agent.query(directive)

class ChromaMemory:
  def __init__(self, chroma_client, k=5):
    self.cc = chroma_client
    self.k = k

  def put(self, input_: str):
    id_num = str(self.cc.count() + 1)
    return self.cc.add(documents=input_text, ids=id_num)

  def get(self, query: str):
    return self.cc.query(query_texts=query, n_results=self.k)

class ReActDaemonLTM:
    def __init__(self, tool_list, llm, sys_prompt, vector_collection:str, k=5, clen=65536, verbose=False, finetune=False, max_iterations=20):
        self.llm = llm
        if finetune:
            self.finetuning_handler = OpenAIFineTuningHandler()
            callback_manager = CallbackManager([self.finetuning_handler])
            self.llm.callback_manager = callback_manager

        # Create a Chroma client and collection
        chroma_client = chromadb.PersistentClient("./vector_memory_db")
        chroma_collection = chroma_client.get_or_create_collection(vector_collection)

        # Set up the ChromaVectorStore and StorageContext
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        vector_memory = VectorMemory.from_defaults(
            vector_store=vector_store,
            embed_model=OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434", ollama_additional_kwargs={"mirostat": 0}),
            retriever_kwargs={"similarity_top_k": k},
        )
        
        self.agent = ReActAgent.from_tools(tool_list, llm=self.llm, context=sys_prompt, verbose=verbose, max_iterations=max_iterations, memory=vector_memory)
        self.max_iterations = max_iterations
        self.agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})

    def execute(self, directive):
        return self.agent.query(directive)
