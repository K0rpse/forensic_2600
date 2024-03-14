import os
import re
import pandas

from main import ForensicExtractor
from termcolor import colored


def test_extract_browser_infos():
    """file = os.environ.get("IMAGE")
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
        print(colored("Done, inserting in full list", "magenta"))
        if not file_list:
            continue
        # Example line : '-/r * 318583-128-4:     $OrphanFiles/ThirdPartyNotices.txt'
        for line in file_list.split('\n'):
            dict_file = {"partition_id": partition["id"]}
            if not line:  # Empty fckng lines
                continue
            # print(line)
            dict_file["file_type"] = re.findall(r"^[^ ]+", line)
            dict_file["metadata_address"] = re.findall(r"[\-0-9()A-z]+(?=:)", line)[0]
            dict_file["file_path"] = line.split('\t')[1]
            while dict_file["file_path"].endswith(" "):
                dict_file["file_path"] = dict_file["file_path"][:-1]
            while dict_file["file_path"].startswith(" "):
                dict_file["file_path"] = dict_file["file_path"][1:]
            full_file_list.append(dict_file)
        print(colored(f"Filelist added for partition {partition['id']}", "magenta"))

    print(colored(f"Total count of files retrieved : {len(full_file_list)}"))"""

    #df = pandas.DataFrame().from_records(full_file_list)
    df = pandas.DataFrame()
    df = pandas.read_csv("export_filenames.csv")

    browser_artifacts = {
        "firefox": {
            "profile": [r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\",
                        r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\"],
            "bookmarks/history": [
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\places.sqlite"],
            "bookmarks_backup": r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\bookmarkbackups",
            "cookies": r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\cookies.sqlite",
            "cache": [r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\cache2\\entries",
                      r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\startupCache"],
            "form_history": [
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\formhistory\.sqlite"],
            "addons/extensions": [
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\addons\.sqlite",
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\extensions\.sqlite"],
            "favicons": [
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\favicons\.sqlite"],
            "settings": [r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\prefs\.js"],
            "logins/passwords": [
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\logins\.json",
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\key[0-9]\.db"],
            "session_data": [
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\sessionstore\.jsonlz4",
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\sessionstore-backups"],
            "downloads": [
                r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\downloads\.sqlite"],
            "thumbnails": [r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\thumbnails"]

        },
        "chrome": {'profile': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default$",
                               r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData$"],
                   'history/downloads': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History$",
                                         r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\History$"],
                   'cookies': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\Cookies$",
                               r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies$"],
                   'cache': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache$",
                             r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\Cache$"],
                   'bookmarks': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\Bookmarks$",
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks$"],
                   'forms_history': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Web Data$"],
                   'favicons': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Favicons$"],
                   'logins': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Login Data$"],
                   'current_sessions/tabs': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\(?:Current Session|Current Tabs|Current Tabs-Last)$"],
                   'previous_sessions/tab': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\(?:Last Session|Last Tabs|Last Tabs-Last)$"],
                   'extensions': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Extensions\\$"],
                   'thumbnails': [
                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\(?:Top Sites|Thumbnails)$"]
                   },
        "edge": {
            "profile_path": [r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,60}\\AC$"],
            "history/cookies/downloads": [
                r"Users\\[^\\]+\\AppData\\Local\\Microsoft\\Windows\\WebCache\\WebCacheV01\.dat$"],
            "settings": [
                r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,60}\\AC\\MicrosoftEdge\\User\\Default\\DataStore\\Data\\[^\\]+\\[^\\]+\\DBStore\\spartan\.edb$"],
            "cache": r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,3}\\AC\\[^\\]+\\MicrosoftEdge\\Cache",
            "last_active_session": [
                r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,60}\\AC\\MicrosoftEdge\\User\\Default\\Recovery\\Active$"]
        }
    }

    interesting_artifacts = {}
    for browser_k in browser_artifacts.keys():
        browser = browser_artifacts[browser_k]
        interesting_artifacts[browser_k] = []
        print(f"================================ {browser_k} ============================================")
        for category_k in browser.keys():
            category = browser[category_k]
            if type(category) is not list:
                category = [category]
            for regex in category:
                print(regex)
                res = df[df.file_path.str.match(regex)]
                if not len(res):
                    regex = regex.replace("\\\\", "/")
                    print(colored(f"Testing with : '{regex}'", "magenta"))
                    res = df[df.file_path.str.match(regex)]
                if len(res):
                    print(colored(f"Matched : '{regex}'", "magenta"))
                    #interesting_files.append()
                    print(res[["file_path"]].values[0])
                    interesting_artifacts[browser_k] += list(res[["file_path"]].values[0])
        print(interesting_artifacts)

        if not os.path.exists("artifacts"):
            os.mkdir("artifacts")


if __name__ == "__main__":
    test_extract_browser_infos()