import os
import subprocess
import yaml
from pathlib import Path
import re
from termcolor import colored


class ForensicExtractor:
    def __init__(self, disk_image_path, output_directory=None):
        self.disk_image_path = disk_image_path
        self.output_directory = output_directory
        self.yaml_config_path = "files_to_extract.yaml"  # Define the path to your YAML config file
        self.current_stderr = ""
        self.patterns = {
            "partition" :  r"006:\s+\d+\s+(\d+)\s+\d+\s+\d+\s+Basic data partition",
            "partition" : {"offset" : 0, "pattern" : r"006:\s+\d+\s+(\d+)\s+\d+\s+\d+\s+Basic data partition"},
            "windows_inode" : r"d\/d (\d+-\d+-\d+):.*Windows*",
            "windows_inode" : {"inode" : 0, "pattern" : r"d\/d (\d+-\d+-\d+):.*Windows*"},
            "system32_inode" : r"d\/d (\d+-\d+-\d+):.*System32*",
            "system32_inode" : {"inode" : 0, "pattern" : r"d\/d (\d+-\d+-\d+):.*System32*"},
            "config_inode" : r"d\/d (\d+-\d+-\d+):.*config*",
            "config_inode" : {"inode" : 0, "pattern" : r"d\/d (\d+-\d+-\d+):.*config*"},
            "system_inode" : r"r\/r (\d+-\d+-\d+):.*SYSTEM\n",
            "system_inode" : {"inode" : 0, "pattern" : r"r\/r (\d+-\d+-\d+):.*SYSTEM\n"},
            "security_inode" : r"r\/r (\d+-\d+-\d+):.*SECURITY\n",
            "security_inode" : {"inode" : 0, "pattern" : r"r\/r (\d+-\d+-\d+):.*SECURITY\n"},
            "software_inode" : r"r\/r (\d+-\d+-\d+):.*SOFTWARE\n",
            "software_inode" : {"inode" : 0, "pattern" : r"r\/r (\d+-\d+-\d+):.*SOFTWARE\n"},
            "sam_inode" : r"r\/r (\d+-\d+-\d+):.*SAM\n",
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
        output = self.run_command(f"fls -o {self.patterns['partition']['offset']} {self.disk_image_path} {self.patterns['windows']['offset']}")

    def extract_hive(self):

        #set partition offset
        output = self.run_command(f"mmls {self.disk_image_path}")
        partition_offset = self.execute_re(self.patterns['partition']['pattern'], output)
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
        self.current_stderr = ""
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error executing command: {command}")
            print(result.stderr)
            self.current_stderr = result.stderr
            return None
        return result.stdout

    def list_partitions(self, fmt="string"):
        assert fmt in ["dict", "string"]
        command = f"mmls {self.disk_image_path}".split(' ')
        partitions_info = self.run_command(command)
        if fmt == "dict":
            parts = []
            for line in partitions_info.split('\n'):
                """
                >>> line.split("  ")
                    ['000:', 'Meta', '', '', '0000000000', ' 0000000000', ' 0000000001', ' Primary Table (#0)']

                """
                if re.match(r"[0-9]{3}:.*", line):
                    vals = line.split("  ")
                    while '' in vals:
                        vals.remove('')
                    _id = int(vals[0].replace(':', ''))
                    parts.append({
                        "id": _id,
                        "slot": vals[1],
                        "start": vals[2].replace(' ', ''),
                        "end": vals[3].replace(' ', ''),
                        "length": vals[4].replace(' ', ''),
                        "description": vals[5],
                    })
            return parts
        return partitions_info

    def list_partition_files(self, partition_number):
        command = f"fls {self.disk_image_path} -r -p {partition_number}".split(' ')
        output = self.run_command(command)
        if "Cannot determine file system type" in self.current_stderr:
            # Offset must be calculated when this error occurs
            parts = self.list_partitions(fmt="dict")
            start_offset = None
            for part in parts:
                if part["id"] == int(partition_number):
                    start_offset = part["start"]
            if start_offset is None:
                print(colored("Alternative partition offset cannot be found by Extractor", "red"))
                return output
            command = f"fls {self.disk_image_path} -r -o {start_offset}".split(' ')
            output = self.run_command(command)
        return output

    def extract_files_of_interest(self, partition_number, files_to_extract):
        return 0

    def extract_forensic_data(self, files_to_extract):
        for file_pattern in files_to_extract:
            return 0
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


if __name__ == "__main__":
    disk_image_path = "disk.E01"
    output_directory = ""
    forensic_extractor = ForensicExtractor(disk_image_path, output_directory)
    forensic_extractor.main()

