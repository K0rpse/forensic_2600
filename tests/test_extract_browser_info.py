import os
import re
import pandas

from main import ForensicExtractor
from termcolor import colored
from pathlib import Path
from data.browser_regex import browser_artifacts



def test_extract_browser_infos():
    file = os.environ.get("IMAGE")
    print(f"File name : {file}")
    extractor = ForensicExtractor(file)
    extractor.extract_browser_info()
    partitions = extractor.list_partitions(fmt="dict")
    for partition in partitions:
        print(partition)

    print(colored("Listing partitions files", "magenta"))

    full_file_list = []
    for partition in partitions:
        print(colored(f"Partition ID : {partition['id']}", "magenta"))
        file_list = extractor.list_partition_files(partition['id'])
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
        print(colored(f"Filelist added for partition {partition['id']}", "magenta"))

    print(colored(f"Total count of files retrieved on filesystem : {len(full_file_list)}"))

    filesystem_df = pandas.DataFrame().from_records(full_file_list)

    interesting_artifacts = []
    for browser_k in browser_artifacts.keys():
        browser = browser_artifacts[browser_k]
        print(colored(f"================================ {browser_k} ============================================", "magenta"))
        for category_k in browser.keys():
            category = browser[category_k]
            if type(category) is not list:
                category = [category]
            for regex in category:
                res = filesystem_df[filesystem_df.file_path.str.match(regex)]
                if not len(res):
                    regex = regex.replace("\\\\", "/")
                    print(colored(f"Searching regex with : '{regex}'", "magenta"))
                    res = filesystem_df[filesystem_df.file_path.str.match(regex)]
                if len(res):
                    print(colored(f"Matched : '{regex}'", "magenta"))
                    print(res[["file_path"]].values[0])
                    for l in res.values:
                        interesting_artifacts.append({"partition_id": l[0], "browser": browser_k, "path": l[-1]})

    output_path = Path("artifacts/browser")
    Path.mkdir(output_path, exist_ok=True, parents=True)

    for artifact in interesting_artifacts:
        output_name = artifact['path'].replace('\\', '_').replace('/', '_').replace(' ', '-')
        with open(f"{output_path}/{output_name}", "wb") as file:
            ret = extractor._extract_file(artifact["partition_id"], artifact["path"], output_fd=file)
        if ret:
            print(colored(f"Successfully fetched file '{artifact['path']}' on partition {artifact['partition_id']}", "green"))
            #with open(f"artifacts/{artifact['path'].split('/')[-1]}", "wb") as file:
            #    file.write(ret.encode())
        else:
            print(colored(f"Failed to fetch file '{artifact['path']}' on partition {artifact['partition_id']}", "red"))



if __name__ == "__main__":
    test_extract_browser_infos()
