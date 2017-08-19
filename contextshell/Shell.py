from contextshell.session_stack.SessionLayer import *
from contextshell.CommandInterpreter import CommandInterpreter
from contextshell.CommandParser import CommandParser
from contextshell.NodePath import *


class Shell:
    """Makes interaction with user painless"""
    def __init__(self, session: SessionLayer):
        self.session = session
        self.interpreter = CommandInterpreter(self.session)
        self.parser = CommandParser()
        self.current_path = NodePath(absolute=True)

    def execute(self, command_line: str):
        command = self.parser.parse(command_line)
        if command is None:
            return None
        if command.target is None:
            command.target = str(self.current_path)
        return self.interpreter.execute(command)

    @staticmethod
    def pretty_print(result):
        print(result)
        # TODO: Rewrite to support new list format (and attributes)
        # if isinstance(result, list):
        #     for r in result:
        #         if isinstance(r, Node):
        #             print("[{}] {}\t = {}".format(r['@index'], r["@name"], r))
        #         else:
        #             print("[{}] {}".format(r['@index'], r))
        # else:
        #     print(result)