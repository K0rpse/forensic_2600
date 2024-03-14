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
                "function": self.select_partition,
                "args": ["selected_partition_number"]
            },
            "unselect": {
                "help": "Unselect partition",
                "function": self.unselect_partition,
                "args": []
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

        self.selected_partition = None

        c = {}
        for k in self.commands:
            c[k] = None
        self.word_completer = NestedCompleter.from_nested_dict(c)
        self.prompt_session = PromptSession(completer=self.word_completer)
        self.start()

    def select_partition(self, new_partition_number):
        self.selected_partition = new_partition_number

    def unselected_partition(self):
        self.selected_partition = None

    def get_command_parser(self, command):
        command = self.commands.get(command)
        if command is None:
            raise RuntimeError(f"Command '{command}' shouldn't be arrived to this function")
        local_parser = argparse.ArgumentParser()
        for arg in command["args"]:
            if arg == "partition_number":
                if self.selected_partition:
                    local_parser.add_argument("partition_number", type=int, required=False)
                else:
                    local_parser.add_argument("partition_number", type=int, required=True)
        return local_parser


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

        try:
            parsed_args = self.get_command_parser(user_command).parse_args(user_args)
        except argparse.ArgumentError as e:
            print("ERROR")
        print(parsed_args)

        """ret = self.commands[user_command]["function"](*user_args)

        if ret is not None:
            print("===============")
            print(ret)"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", action="store", required=True)
    parser.add_argument("--output-file", "-o", action="store", required=False)
    args = parser.parse_args()


    Cli(args.file, args.output_file)
