import subprocess
import time
import yaml
import os

def _get_container_names_from_compose(file_path):
    with open(file_path, 'r') as file:
        compose_data = yaml.safe_load(file)
    
    # Extracting service names from the 'services' section
    container_names = list(compose_data.get('services', {}).keys())
    return container_names

class DockerBackend:
    def __init__(self, compose_path, startup_time=10, service_name="kali-rolling"):
        self.compose_path = compose_path
        self.startup_time = startup_time
        self.service_name = service_name
        
    def start(self):
        subprocess.run(['sudo', 'docker', 'compose', '-f', self.compose_path, 'up', '-d'])
        time.sleep(self.startup_time)

    def stop(self):
        subprocess.run(['sudo', 'docker', 'compose', '-f', self.compose_path, 'down'])

class ExternalBackend:
    def __init__(self, verbose=True):
        self.verbose = verbose

    def active(self):
        print("External backend, you must monitor status yourself.")
        return True

    def start(self):
        if self.verbose:
            print("External Backend, you must start it up yourself.")

    def stop(self):
        if self.verbose:
            print("External Backend, you must shut it down yourself.")