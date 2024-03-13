import os
import subprocess
import yaml
from pathlib import Path

class ForensicExtractor:
    def __init__(self, disk_image_path, output_directory):
        self.disk_image_path = disk_image_path
        self.output_directory = output_directory
        self.yaml_config_path = "files_to_extract.yaml"  # Define the path to your YAML config file


    def extract_file(self):
        return 0

    def extract_browser_info(self):
        return 0
    
    def extract_security_log_info(self):
        return 0

    def extract_mft(self):
        return 0

    def run_command(self, command):
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error executing command: {command}")
            print(result.stderr)
            return None
        return result.stdout

    def list_partitions(self):
        command = ["mmls", self.disk_image_path]
        partitions_info = self.run_command(command)
        return partitions_info

    def list_partition_files(self, partition_number):
        command = ["fls", self.disk_image_path, f"-r", f"-p{partition_number}"]
        partition_files = self.run_command(command)
        return partition_files

    def extract_files_of_interest(self, partition_number, files_to_extract):
        return 0

    def extract_forensic_data(self, files_to_extract):
        for file_pattern in files_to_extract:
            # Use Eric Zimmerman or RegRipper tools to extract data
            # Implement your logic here

    def main(self):
        partitions_info = self.list_partitions()
        # Choose the right partition based on your logic
        chosen_partition = 1
        partition_files = self.list_partition_files(chosen_partition)

        with open(self.yaml_config_path, "r") as config_file:
            config_data = yaml.safe_load(config_file)

        files_to_extract = config_data.get("files_to_extract", [])
        self.extract_files_of_interest(chosen_partition, files_to_extract)

        self.extract_forensic_data(files_to_extract)



disk_image_path = "disk.E01"
output_directory = ""
forensic_extractor = ForensicExtractor(disk_image_path, output_directory)
forensic_extractor.main()
