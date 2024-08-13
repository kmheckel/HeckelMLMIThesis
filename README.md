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