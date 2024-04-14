import os
import subprocess
import yaml
from pathlib import Path
import re
# from termcolor import colored


class ForensicExtractor:
    def __init__(self, disk_image_path, output_directory=None):
        self.disk_image_path = disk_image_path
        self.output_directory = output_directory
        self.data_partition_offset = ""
        self.yaml_config_path = "files_to_extract.yaml"  # Define the path to your YAML config file
        self.current_stderr = ""
        self.patterns = {
            "partition" :  r"006:\s+\d+\s+(\d+)\s+\d+\s+\d+\s+Basic data partition",
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
            "sam_inode" : {"inode" : 0, "pattern": r"r\/r (\d+-\d+-\d+):.*SAM\n"},
            'users_inode' : {"inode": 0, "pattern":  r"d\/d (\d+-\d+-\d+):.*Users*"},
            'ntuser_data_inode' : r"r\/r (\d+-\d+-\d+):.*NTUSER.DAT*",
            "random_inode" : r"d\/d (\d+-\d+-\d+):",
            "mft": r"002:\s+\d+\s+(\d+)\s+\d+\s+\d+\s+NTFS / exFAT(0x07)",
            "mft_inode": r"r\/r (\d+-\d+-\d+):.*$MFT*",
            "mft_inode": {"inode" : 0, "pattern" :r"r\/r (\d+-\d+-\d+):.*$MFT*"}
        }


    def execute_re(self, pattern, data):
        match = re.search(pattern, data)
        if match == None:
            print(f"FAIL MATCH\n   [+] Data: {data}\n   [+] pattern: {pattern}")
            return None
        return match.group(1)



    def init_offset_partition_data(self):
        output = self.run_command(f"mmls {self.disk_image_path}")
        self.data_partition_offset = self.execute_re(self.patterns["partition"], output)
        print(self.data_partition_offset)

    def get_offset_partition_data(self):
        return self.data_partition_offset

    def get_windows_inode(self):
        windows_ = self.patterns["pattern"]
        output = self.run_command(f"fls -o {self.patterns['partition']} {self.disk_image_path} {self.patterns['windows']['offset']}")

    def get_user_hive(self):

        ls_root = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path}")
        #print(ls_root)
        users_inode = self.execute_re(self.patterns['users_inode']['pattern'], ls_root)
        ls_users = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path} {users_inode}").split("\n")
        i=0
        for user in ls_users:
            if ("All Users" not in user) and ("Default User" not in user) and ("desktop.ini" not in user) and ("Public" not in user):
                #print(user)
                user_inode = self.execute_re(self.patterns['random_inode'], user)
                if user_inode != None:
                    #print(user_inode)
                    ls_user = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path} {user_inode}")
                    
                    nt_user_data_inode = self.execute_re(self.patterns["ntuser_data_inode"], ls_user)
                    
                    os.system(f"icat -o {self.data_partition_offset} {disk_image_path} {nt_user_data_inode} > output/ntuser{str(i)}.dat")
                    i+=1

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

        system_inode = self.execute_re(self.patterns["system_inode"]["pattern"], output_config)

        security_inode = self.execute_re(self.patterns["security_inode"]["pattern"], output_config)

        software_inode = self.execute_re(self.patterns["software_inode"]["pattern"], output_config)

        sam_inode = self.execute_re(self.patterns["sam_inode"]["pattern"], output_config)

        print(f"system inode: {system_inode}\nsecurity inode: {security_inode}\nsoftware_inode: {software_inode}\nsam inode: {sam_inode}")

        print(partition_offset, disk_image_path)

        print(f"icat -o {partition_offset} {disk_image_path} {system_inode} > output/SYSTEM")
        os.system(f"icat -o {partition_offset} {disk_image_path} {system_inode} > output/SYSTEM")
        os.system(f"icat -o {partition_offset} {disk_image_path} {security_inode} > output/SECURITY")
        os.system(f"icat -o {partition_offset} {disk_image_path} {software_inode} > output/SOFTWARE")
        os.system(f"icat -o {partition_offset} {disk_image_path} {sam_inode} > output/SAM")
        

    def extract_file(self, partition_number, file_path, output_fd=None):
        parts = self.list_partitions(fmt="dict")
        start_offset = None
        for part in parts:
            if part["id"] == partition_number:
                start_offset = part["start"]
        if start_offset is None:
            raise ValueError(colored(f"Partition number {partition_number} offset cannot be count", "red"))

        command = f"fcat -o {start_offset} {file_path} {self.disk_image_path}"
        command = command.split(' ')
        output = self.run_command(command, stdout=output_fd, text=not bool(output_fd))
        return output

    def extract_browser_info(self):
        return 0

    def extract_security_log_info(self):
        return 0

    def extract_mft(self):

        #get ntfs partition offset
        output = self.run_command(f"mmls {self.disk_image_path}")
        mft_offset = self.execute_re(self.patterns['mft']['pattern'], output)
        self.patterns["mft"]["offset"] = mft_offset

        #set all inode
        output = self.run_command(f"fls -o {mft_offset} {self.disk_image_path}")
        mft_inode = self.execute_re(self.patterns["mft_inode"]['pattern'], output)

        os.system(f"icat -o {mft_offset} {disk_image_path} {mft_inode} > output/MFT")


    def run_command(self, command, stdout=subprocess.PIPE, text=True) -> str | bool | None:
        self.current_stderr = ""
        result = subprocess.run(command, stdout=stdout, stderr=subprocess.PIPE, text=text)
        if result.returncode != 0:
            print(f"Error executing command: {command}")
            print(result.stderr)
            self.current_stderr = result.stderr
            return None
        if stdout == subprocess.PIPE:
            return result.stdout
        else:
            return result.returncode == 0

    def list_partitions(self, fmt="string"):
        assert fmt in ["dict", "string"]
        command = f"mmls {self.disk_image_path}".split(' ')
        partitions_info = self.run_command(command)


        if fmt == "dict" and partitions_info is not None:
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
        command = f"fls {self.disk_image_path} -r -l -p {partition_number}".split(' ')
        output = self.run_command(command)
        if "Cannot determine file system type" in self.current_stderr:
            print(colored("Trying using offset", "blue"))
            # Offset must be calculated when this error occurs
            parts = self.list_partitions(fmt="dict")
            start_offset = None
            for part in parts:
                if part["id"] == int(partition_number):
                    start_offset = part["start"]
            if start_offset is None:
                print(colored("Alternative partition offset cannot be found by Extractor", "red"))
                return output
            command = f"fls {self.disk_image_path} -r -p -o {start_offset}".split(' ')
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

        """
        
        partitions_info = self.list_partitions()
        # Choose the right partition based on your logic
        chosen_partition = 1
        partition_files = self.list_partition_files(chosen_partition)

        
        with open(self.yaml_config_path, "r") as config_file:
            config_data = yaml.safe_load(config_file)

        files_to_extract = config_data.get("files_to_extract", [])
        self.extract_files_of_interest(chosen_partition, files_to_extract)

        self.extract_forensic_data(files_to_extract)
        """
        self.init_offset_partition_data()
        self.get_user_hive()

        


if __name__ == "__main__":
    disk_image_path = "disk.E01"
    output_directory = ""
    forensic_extractor = ForensicExtractor(disk_image_path, output_directory)
    forensic_extractor.main()
