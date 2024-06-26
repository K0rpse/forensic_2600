import os
import subprocess
import re
import argparse
from pathlib import Path
import pandas
import logging
import coloredlogs
from data.browser_regex import browser_artifacts

coloredlogs.install(level=logging.DEBUG)


class ForensicExtractor:
    def __init__(self, disk_image_path, output_directory="artifacts"):
        self.logger = logging.getLogger(__name__)
        self.disk_image_path = disk_image_path
        self.output_directory = output_directory
        Path.mkdir(Path(self.output_directory), exist_ok=True, parents=True)
        self.patterns = {
            "partitionv1": r"006:\s+\d+\s+(\d+)\s+\d+\s+\d+\s+Basic data partition",
            "partition": r"^[0-9]{1,3}: {2}[^ ]+ +([0-9]{10}) {3}[0-9]{10} {3}[0-9]{10} {3}(NTFS.*|Basic data partition)$",
            'users_inode' : {"inode": 0, "pattern":  r"d\/d (\d+-\d+-\d+):.*Users*"},
            'ntuser_data_inode' : r"r\/r (\d+-\d+-\d+):.*NTUSER.DAT*",
            "random_inode" : r"d\/d (\d+-\d+-\d+):"
        }

        self.system_logs_paths = {
            "Windows" :"d",
            "System32": "d",
            "winevt": "d",
            "Logs": "d",
            "Security.evtx": "r",
            "System.evtx": "r"
        }

        self.system_hive_paths = {
             "Windows" : "d",
             "System32" : "d",
             "config" : "d",
             "SYSTEM": "r",
             "SOFTWARE": "r",
             "SECURITY": "r",
             "SAM": "r"
        }
        self.yaml_config_path = "files_to_extract.yaml"  # Define the path to your YAML config file
        self.current_stderr = ""


        
        self.data_partition_offset = self._init_offset_partition_data()

        
    def _init_offset_partition_data(self):
       output = self.run_command(f"mmls {self.disk_image_path}")
       data_partition_offset = self._execute_re(self.patterns["partitionv1"], output)
       assert data_partition_offset
       return data_partition_offset

    @staticmethod
    def _execute_re(pattern, data):
        print("log: ", pattern, data)
        match = re.search(pattern, data)
        if match == None:
            print(f"FAIL MATCH\n   [+] Data: {data}\n   [+] pattern: {pattern}")
            return None
        return match.group(1)
    

    def extract_data(self, paths):
        output = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path}")
        for name in paths:
            pattern = self.get_pattern(name, paths[name])
            inode = self._execute_re(pattern, output)
            if paths[name] == "d":
                output = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path} {inode}")
            else:
                os.system(f"icat -o {self.data_partition_offset} {self.disk_image_path} {inode} > {self.output_directory}/{name}")

    def get_pattern(self, name: str, is_directory="d"):
        return r"d\/d (\d+-\d+-\d+):.*" + name + r"*" if is_directory=="d" else r"r\/r (\d+-\d+-\d+):.*"+name+"*"


    def extract_mft(self):

        # get ntfs partition offset
        output = self.run_command(f"mmls {self.disk_image_path}")
        mft_offset = self.execute_re(self.patterns['mft']['pattern'], output)
        self.patterns["mft"]["offset"] = mft_offset

        # set all inode
        output = self.run_command(f"fls -o {mft_offset} {self.disk_image_path}")
        mft_inode = self.execute_re(self.patterns["mft_inode"]['pattern'], output)

        os.system(f"icat -o {mft_offset} {self.disk_image_path} {mft_inode} > output/MFT")

    def run_command(self, command, stdout=subprocess.PIPE, text=True) -> str | bool | None:
        self.current_stderr = ""
        result = subprocess.run(command, stdout=stdout, shell=True, stderr=subprocess.PIPE, text=text)
        if result.returncode != 0:
            self.logger.warning(f"Error executing command: {command}")
            self.logger.warning(result.stderr)
            self.current_stderr = result.stderr
            return None
        if stdout == subprocess.PIPE:
            return result.stdout
        else:
            return result.returncode == 0


    # def _get_offset_partition_data(self):
    #    return self.data_partition_offset

    def get_data_partitions_offsets(self) -> list:
        output = self.run_command(f"mmls {self.disk_image_path}".split(' '))
        res = re.findall(self.patterns["partition"], output, flags=re.RegexFlag.M)
        # Re groups extract
        offsets = [x[0].replace(' ', '') for x in res]
        if res:
            return offsets
        else:
            return []

    def extract_user_hive(self):
        ls_root = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path}")
        users_inode = self._execute_re(self.patterns['users_inode']['pattern'], ls_root)
        ls_users = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path} {users_inode}").split("\n")
        i=0
        for user in ls_users:
            if ("All Users" not in user) and ("Default User" not in user) and ("desktop.ini" not in user) and ("Public" not in user):
                #print(user)
                user_inode = self._execute_re(self.patterns['random_inode'], user)
                if user_inode != None:
                    #print(user_inode)
                    ls_user = self.run_command(f"fls -o {self.data_partition_offset} {self.disk_image_path} {user_inode}")
                    nt_user_data_inode = self._execute_re(self.patterns["ntuser_data_inode"], ls_user)
                    print(f"icat -o {self.data_partition_offset} {self.disk_image_path} {nt_user_data_inode} > output/ntuser{str(i)}.dat")
                    os.system(f"icat -o {self.data_partition_offset} {self.disk_image_path} {nt_user_data_inode} > output/ntuser{str(i)}.dat")
                    i+=1

    def _extract_file(self, partition_number, file_path, output_fd=None):
        parts = self.list_partitions(fmt="dict")
        start_offset = None
        for part in parts:
            if part["id"] == partition_number:
                start_offset = part["start"]
        if start_offset is None:
            raise ValueError(f"Partition number {partition_number} offset cannot be count")

        command = f"fcat -o {start_offset} {file_path} {self.disk_image_path}"
        command = command.split(' ')
        output = self.run_command(command, stdout=output_fd, text=not bool(output_fd))
        return output

    def extract_browser_info(self):
        partitions = self.list_partitions(fmt="dict")
        self.logger.info("Starting browser artifacts extraction")

        self.logger.debug("Listing partitions files")

        full_file_list = []
        for partition in partitions:
            self.logger.debug(f"Partition ID : {partition['id']}")
            file_list = self.list_partition_files(partition['id'])
            if not file_list:
                continue
            # Example line : '-/r * 318583-128-4:     $OrphanFiles/ThirdPartyNotices.txt'
            for line in file_list.split('\n'):
                dict_file = {"partition_id": partition["id"]}
                if not line:  # Empty fckng lines
                    continue
                # print(line)
                dict_file["partition_number"] = partition["id"]
                dict_file["file_type"] = re.findall(r"^[^ ]+", line)
                dict_file["metadata_address"] = re.findall(r"[\-0-9()A-z]+(?=:)", line)[0]
                dict_file["file_path"] = line.split('\t')[1]
                while dict_file["file_path"].endswith(" "):
                    dict_file["file_path"] = dict_file["file_path"][:-1]
                while dict_file["file_path"].startswith(" "):
                    dict_file["file_path"] = dict_file["file_path"][1:]
                full_file_list.append(dict_file)
            self.logger.debug(f"Filelist added for partition {partition['id']}")

        self.logger.info(f"Total count of files retrieved on filesystem : {len(full_file_list)}")

        filesystem_df = pandas.DataFrame().from_records(full_file_list)

        interesting_artifacts = []
        for browser_k in browser_artifacts.keys():
            browser = browser_artifacts[browser_k]
            self.logger.info(
                f"================================ {browser_k} ============================================")
            for category_k in browser.keys():
                category = browser[category_k]
                if type(category) is not list:
                    category = [category]
                for regex in category:
                    res = filesystem_df[filesystem_df.file_path.str.match(regex)]
                    if not len(res):
                        regex = regex.replace("\\\\", "/")
                        self.logger.debug(f"Searching regex with : '{regex}'")
                        res = filesystem_df[filesystem_df.file_path.str.match(regex)]
                    if len(res):
                        self.logger.info(f"Matched : '{regex}' ({res[['file_path']].values[0]})")
                        for l in res.values:
                            interesting_artifacts.append({"partition_id": l[0], "browser": browser_k, "path": l[-1]})

        output_path = Path(f"{self.output_directory}/browser")
        Path.mkdir(output_path, exist_ok=True, parents=True)

        for artifact in interesting_artifacts:
            output_name = artifact['path'].replace('\\', '_').replace('/', '_').replace(' ', '-')
            with open(f"{output_path}/{output_name}", "wb") as file:
                ret = self._extract_file(artifact["partition_id"], artifact["path"], output_fd=file)
            if ret:
                self.logger.info(
                    f"Successfully fetched file '{artifact['path']}' on partition {artifact['partition_id']}")
            else:
                self.logger.error(f"Failed to fetch file '{artifact['path']}' on partition {artifact['partition_id']}")

    def extract_security_log_info(self):
        return 0

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
            self.logger.debug("Trying using offset")
            # Offset must be calculated when this error occurs
            parts = self.list_partitions(fmt="dict")
            start_offset = None
            for part in parts:
                if part["id"] == int(partition_number):
                    start_offset = part["start"]
            if start_offset is None:
                self.logger.error("Alternative partition offset cannot be found by Extractor")
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
        # self._init_offset_partition_data()
        # self.extract_browser_info()

        """
        self.init_offset_partition_data()
        self.extract_user_hive()
        self.extract_data(self.system_hive_paths)
        self.extract_data(self.system_logs_paths)
        """


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--disk", "-d", action="store", required=True)
    parser.add_argument("--output-dir", "-O", action="store", required=False, default="artifacts")
    parser.add_argument("--extract-user-hive", action="store_true")
    parser.add_argument("--extract-system-hive", action="store_true")
    parser.add_argument("--extract-browser-data", action="store_true")
    parser.add_argument("--extract-system-logs", action="store_true")

    args = parser.parse_args()
    forensic_extractor = ForensicExtractor(os.path.abspath(args.disk), args.output_dir)

    if args.extract_system_hive:
        forensic_extractor.extract_data(forensic_extractor.system_hive_paths)
    if args.extract_system_logs:
        forensic_extractor.extract_data(forensic_extractor.system_logs_paths)
    if args.extract_user_hive:
        forensic_extractor.extract_user_hive()
