# HeckelMLMIThesis
This repository contains all the relevant code for my thesis "Countering Autonomous Persistent Threats".

It contains three subdirectories:

1. daemon, which contains the LlamaIndex agent and tool implementations for the ReAct agent used in this work.

2. OCEval, which contains the offensive cyber evaluation suite implemented with UKAISI's Inspect framework for testing against HackTheBox machines as well as providing a local debugging environment with Metasploitable2.

3. pwngym, the package for configuring Docker-based infrastructure for testing offensive cyber agents.


# Installation:

First install the requirements:

```
pip install -r requirements.txt
```

Next, pip install the daemon and pwngym libraries:

```
pip install -e ./daemon
```

```
pip install -e ./pwngym
```


# HTB access and API Keys

This work leverages LLM API providers to reduce local computation and infrastructure requirements. 

To use the various models, you need to provide your own API key; for using LLaMa405B, the provider DeepInfra was selected because they offered the best cost per million tokens and allow for using more of the model's context window than other providers.

To test against HTB machines, you need to create an account:

https://account.hackthebox.com/register

Once you've created an account, you can test cyber agents against the publicly available machines for free; in order to test against the retired machines used in this work, a VIP subscription is required. 

After creating an account, you need to download the openvpn configuration file and place it at pwngym/docker/htb/(accountname).ovpn before building the docker containers.
Note that the .ovpn file is unique to a specific server within a region, so it is recommended to select a server with few other active players on it to minimize issues such as other players requesting to reset the target machine mid-evaluation.

To run evaluations efficiently, installation of the Inspect AI VSCode extension is strongly recommended as it allows for passing arguments to the tasks via a sidebar menu.

Note that Ollama is required for the model grading mechanism; while Mistral7B was used during the experiments, a lighter alternative such as Gemma2B could be used on computers which lack a discrete GPU.

# Examining Logs from Experiments

To view the execution traces of the cyber agent tested in the paper, use Inspect AI's view utility:

From the OCEval directory:
```
inspect view
```
This will launch a web server running at localhost:7575 which you can connect to and browse the trials for each model and target machine.

# Try Locally:

Install Ollama:
```
curl -fsSL https://ollama.com/install.sh | sh
```

Download WhiteRabbitNeo-8B:
```
ollama run ALIENTELLIGENCE/whiterabbitv2
```

Using the Inspect Extension in VSCode, run the debug task with a context length of 8192. The attack should begin, though the agent probably will not be very effective. Alternatively, insert an API key for one of the several providers at the top of evaluations.py and specify an appropriate model_name instead.