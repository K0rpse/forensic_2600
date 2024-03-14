from prompt_toolkit import prompt, history, PromptSession
from prompt_toolkit.completion import WordCompleter
from main import ForensicExtractor
import argparse
from prompt_toolkit.completion import NestedCompleter

class Cli:
    def __init__(self, disk_image_path, output_directory):
        self.forensic_extractor = ForensicExtractor(disk_image_path, output_directory)
        self.commands = {
            "help": {
                "function": self.help,
                "help": "Display this help ^^",
                "args": []
            },
            "exit": {
                "help": "Quit",
                "function": exit,
                "args": []
            },
            "select": {
                "help": "Select partition",
                "args": ["partition"]
            },
            "lspart": {
                "help": "List partitions",
                "args": [],
                "function": self.forensic_extractor.list_partitions
            },
            "lspartfiles": {
                "help": "List partitions files",
                "args": ["partition_number"],
                "function": self.forensic_extractor.list_partition_files
            }
        }

        c = {}
        for k in self.commands:
            c[k] = None
        self.word_completer = NestedCompleter.from_nested_dict(c)
        self.prompt_session = PromptSession(completer=self.word_completer)
        self.start()

    def help(self, command=None):
        for command_k in self.commands.keys():
            if command is None or command == command_k:
                print(f"{command_k}", end="")
                for arg in self.commands[command_k]["args"]:
                    print(f" [{arg}]", end="")
                print(f" : {self.commands[command_k]['help']}", end="")
                print()

    def start(self):
        print("=============Forensic extractor V1.0=============")
        print("Enter 'help' for help")
        while True:
            command = self.prompt_session.prompt("> ")
            self.parse_command(command)

    def parse_command(self, user_input: str):
        if not user_input:
            return
        user_command = user_input.split(' ')[0]
        if len(user_input.split(' ')) > 1:
            user_args = user_input.split(' ')[1:]
        else:
            user_args = []

        if user_command not in self.commands.keys():
            print(f"Command '{user_command}' is not known")
            return

        if len(self.commands[user_command]["args"]) != len(user_args):
            if len(self.commands[user_command]["args"]) > len(user_args):
                print(f"Missing argument(s) for command '{user_command}'")
            elif len(self.commands[user_command]["args"]) < len(user_args):
                print(user_args)
                print(f"Too many argument(s) for command '{user_command}'")
            self.help(user_command)
            return

        ret = self.commands[user_command]["function"](*user_args)

        if ret is not None:
            print("===============")
            print(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", action="store", required=True)
    parser.add_argument("--output-file", "-o", action="store", required=False)
    args = parser.parse_args()


    Cli(args.file, args.output_file)
