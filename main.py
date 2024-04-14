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
        self.data_partition_offset = ""
        self.yaml_config_path = "files_to_extract.yaml"  # Define the path to your YAML config file
        self.current_stderr = ""
        self.patterns = {
            #"partition": r"006:\s+\d+\s+(\d+)\s+\d+\s+\d+\s+Basic data partition",
            "partition": r"^[0-9]{1,3}: {2}[^ ]+ +([0-9]{10}) {3}[0-9]{10} {3}[0-9]{10} {3}(NTFS.*|Basic data partition)$",
            "windows_inode": r"d\/d (\d+-\d+-\d+):.*Windows*",
            "windows_inode": {"inode": 0, "pattern": r"d\/d (\d+-\d+-\d+):.*Windows*"},
            "system32_inode": r"d\/d (\d+-\d+-\d+):.*System32*",
            "system32_inode": {"inode": 0, "pattern": r"d\/d (\d+-\d+-\d+):.*System32*"},
            "config_inode": r"d\/d (\d+-\d+-\d+):.*config*",
            "config_inode": {"inode": 0, "pattern": r"d\/d (\d+-\d+-\d+):.*config*"},
            "system_inode": r"r\/r (\d+-\d+-\d+):.*SYSTEM\n",
            "system_inode": {"inode": 0, "pattern": r"r\/r (\d+-\d+-\d+):.*SYSTEM\n"},
            "security_inode": r"r\/r (\d+-\d+-\d+):.*SECURITY\n",
            "security_inode": {"inode": 0, "pattern": r"r\/r (\d+-\d+-\d+):.*SECURITY\n"},
            "software_inode": r"r\/r (\d+-\d+-\d+):.*SOFTWARE\n",
            "software_inode": {"inode": 0, "pattern": r"r\/r (\d+-\d+-\d+):.*SOFTWARE\n"},
            "sam_inode": r"r\/r (\d+-\d+-\d+):.*SAM\n",
            "sam_inode": {"inode": 0, "pattern": r"r\/r (\d+-\d+-\d+):.*SAM\n"},
            'users_inode': {"inode": 0, "pattern": r"d\/d (\d+-\d+-\d+):.*Users*"},
            'ntuser_data_inode': r"r\/r (\d+-\d+-\d+):.*NTUSER.DAT*",
            "random_inode": r"d\/d (\d+-\d+-\d+):"
        }

    @staticmethod
    def _execute_re(pattern, data):
        match = re.search(pattern, data)
        if match == None:
            print(f"FAIL MATCH\n   [+] Data: {data}\n   [+] pattern: {pattern}")
            return None
        return match.group(1)

    def run_command(self, command, stdout=subprocess.PIPE, text=True) -> str | bool | None:
        self.current_stderr = ""
        result = subprocess.run(command, stdout=stdout, stderr=subprocess.PIPE, text=text)
        if result.returncode != 0:
            self.logger.warning(f"Error executing command: {command}")
            self.logger.warning(result.stderr)
            self.current_stderr = result.stderr
            return None
        if stdout == subprocess.PIPE:
            return result.stdout
        else:
            return result.returncode == 0

    #def _init_offset_partition_data(self):
    #    output = self.run_command(f"mmls {self.disk_image_path}".split(' '))
    #    self.data_partition_offset = self._execute_re(self.patterns["partition"], output)
    #    assert self.data_partition_offset

    #def _get_offset_partition_data(self):
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


    def get_user_hive(self):
        output_path = f"{self.output_directory}/user_hive"
        Path.mkdir(Path(output_path), exist_ok=True, parents=True)

        data_partitions = self.get_data_partitions_offsets()
        for i_part in range(len(data_partitions)):
            offset = data_partitions[i_part]

            ls_root = self.run_command(f"fls -o {offset} {self.disk_image_path}".split(' '))
            users_inode = self._execute_re(self.patterns['users_inode']['pattern'], ls_root)
            if users_inode is None:
                self.logger.warning(f"Data partition at offset {offset} doesn't contain Users folder, skipping")
                continue
            ls_users = self.run_command(f"fls -o {offset} {self.disk_image_path} {users_inode}".split(" ")).split('\n')
            i_user = 0
            for user in ls_users:
                if ("All Users" not in user) and ("Default User" not in user) and ("desktop.ini" not in user) and (
                        "Public" not in user):
                    user_inode = self._execute_re(self.patterns['random_inode'], user)
                    if user_inode != None:
                        print(user)
                        user_name = re.findall(r"d\/d (\d+-\d+-\d+):\t(.*)$", user, flags=re.RegexFlag.M)[0][1]
                        ls_user = self.run_command(f"fls -o {offset} {self.disk_image_path} {user_inode}".split(' '))

                        nt_user_data_inode = self._execute_re(self.patterns["ntuser_data_inode"], ls_user)

                        filename = f"ntuser_{user_name}_{i_part}.dat"
                        os.system(
                            f"icat -o {offset} {self.disk_image_path} {nt_user_data_inode}"
                            f" > {output_path}/{filename}")
                        i_user += 1

    def _extract_hive(self):

        # set partition offset
        output = self.run_command(f"mmls {self.disk_image_path}")
        partition_offset = self._execute_re(self.patterns['partition']['pattern'], output)
        self.patterns["partition"]["offset"] = partition_offset

        # set all inode
        output = self.run_command(f"fls -o {partition_offset} {self.disk_image_path}")
        windows_inode = self._execute_re(self.patterns["windows_inode"]['pattern'], output)
        output = self.run_command(f"fls -o {partition_offset} {self.disk_image_path} {windows_inode}")
        system32_inode = self._execute_re(self.patterns["system32_inode"]["pattern"], output)
        output = self.run_command(f"fls -o {partition_offset} {self.disk_image_path} {system32_inode}")
        config_inode = self._execute_re(self.patterns["config_inode"]["pattern"], output)
        output_config = self.run_command(f"fls -o {partition_offset} {self.disk_image_path} {config_inode}")
        system_inode = self._execute_re(self.patterns["system_inode"]["pattern"], output_config)
        security_inode = self._execute_re(self.patterns["security_inode"]["pattern"], output_config)
        software_inode = self._execute_re(self.patterns["software_inode"]["pattern"], output_config)
        sam_inode = self._execute_re(self.patterns["sam_inode"]["pattern"], output_config)

        self.logger.info(
            f"system inode: {system_inode}\nsecurity inode: {security_inode}\nsoftware_inode: {software_inode}\nsam inode: {sam_inode}")

        self.logger.debug(partition_offset, self.disk_image_path)

        os.system(f"icat -o {partition_offset} {self.disk_image_path} {system_inode} > {self.output_directory}/SYSTEM")
        os.system(f"icat -o {partition_offset} {self.disk_image_path} {security_inode} > {self.output_directory}/SECURITY")
        os.system(f"icat -o {partition_offset} {self.disk_image_path} {software_inode} > {self.output_directory}/SOFTWARE")
        os.system(f"icat -o {partition_offset} {self.disk_image_path} {sam_inode} > {self.output_directory}/SAM")

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
            self.logger.info(f"================================ {browser_k} ============================================")
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
                self.logger.info(f"Successfully fetched file '{artifact['path']}' on partition {artifact['partition_id']}")
            else:
                self.logger.error(f"Failed to fetch file '{artifact['path']}' on partition {artifact['partition_id']}")

    def extract_security_log_info(self):
        return 0

    def extract_mft(self):
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
        #self._init_offset_partition_data()
        self.get_user_hive()
        #self.extract_browser_info()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--disk", "-d", action="store", required=True)
    parser.add_argument("--output-dir", "-O", action="store", required=False, default="artifacts")
    args = parser.parse_args()
    forensic_extractor = ForensicExtractor(os.path.abspath(args.disk), args.output_dir)
    forensic_extractor.main()
