import os
import subprocess
from pathlib import Path
import re

class ForensicExtractor:
    def __init__(self, disk_image_path, output_directory):
        self.disk_image_path = disk_image_path
        self.output_directory = output_directory
        self.yaml_config_path = "files_to_extract.yaml"  # Define the path to your YAML config file
        self.patterns = {
            "partition" : {"offset" : 0, "pattern" : r"006:\s+\d+\s+(\d+)\s+\d+\s+\d+\s+Basic data partition"},
            "windows_inode" : {"inode" : 0, "pattern" : r"d\/d (\d+-\d+-\d+):.*Windows*"},
            "system32_inode" : {"inode" : 0, "pattern" : r"d\/d (\d+-\d+-\d+):.*System32*"},
            "config_inode" : {"inode" : 0, "pattern" : r"d\/d (\d+-\d+-\d+):.*config*"},
            "system_inode" : {"inode" : 0, "pattern" : r"r\/r (\d+-\d+-\d+):.*SYSTEM\n"},
            "security_inode" : {"inode" : 0, "pattern" : r"r\/r (\d+-\d+-\d+):.*SECURITY\n"},
            "software_inode" : {"inode" : 0, "pattern" : r"r\/r (\d+-\d+-\d+):.*SOFTWARE\n"},
            "sam_inode" : {"inode" : 0, "pattern": r"r\/r (\d+-\d+-\d+):.*SAM\n"}
        }

    def execute_re(self, pattern, data):
        match = re.search(pattern, data)
        if match == None:
            print("Fail match")
            return None
        return match.group(1)


        
    def get_offset_partition_data(self):
        output = self.run_command(f"mmls {self.disk_image_path}")
        self.patterns["partition"]["offset"] = self.execute_re(self.patterns["partition"]["pattern"], output)
        return self.patterns["partition"]["offset"]

    def get_windows_inode(self):
        windows_ = self.patterns["pattern"]
        output = self.run_command(f"fls -o {self.patterns["partition"]["offset"]} {self.disk_image_path} {self.patterns["windows"]["offset"]}")

    def extract_hive(self):

        #set partition offset
        output = self.run_command(f"mmls {self.disk_image_path}")
        partition_offset = self.execute_re(self.patterns["partition"]["pattern"], output)
        self.patterns["partition"]["offset"] = partition_offset


        #set all inode
        output = self.run_command(f"fls -o {partition_offset} {self.disk_image_path}")
        windows_inode = self.execute_re(self.patterns["windows_inode"]['pattern'], output)

        #print(f"windows inode: {windows_inode}")


        output = self.run_command(f"fls -o {partition_offset} {self.disk_image_path} {windows_inode}")

        system32_inode = self.execute_re(self.patterns["system32_inode"]["pattern"], output)

        #print(f"system32 inode: {system32_inode}")       

        output = self.run_command(f"fls -o {partition_offset} {self.disk_image_path} {system32_inode}")
        config_inode = self.execute_re(self.patterns["config_inode"]["pattern"], output)

        #print(f"config inode {config_inode}")

        output_config = self.run_command(f"fls -o {partition_offset} {self.disk_image_path} {config_inode}")

        #print(output_config)

        system_inode = self.execute_re(self.patterns["system_inode"]["pattern"], output_config)

        security_inode = self.execute_re(self.patterns["security_inode"]["pattern"], output_config)

        software_inode = self.execute_re(self.patterns["software_inode"]["pattern"], output_config)

        sam_inode = self.execute_re(self.patterns["sam_inode"]["pattern"], output_config)

        print(f"system inode: {system_inode}\nsecurity inode: {security_inode}\nsoftware_inode: {software_inode}\nsam inode: {sam_inode}")

        os.system(f"icat -o {partition_offset} {disk_image_path} {system_inode} > output/SYSTEM")
        os.system(f"icat -o {partition_offset} {disk_image_path} {security_inode} > output/SECURITY")
        os.system(f"icat -o {partition_offset} {disk_image_path} {software_inode} > output/SOFTWARE")
        os.system(f"icat -o {partition_offset} {disk_image_path} {sam_inode} > output/SAM")

        
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
            return 0

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
print(forensic_extractor.extract_hive())
