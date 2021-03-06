from collections.__init__ import OrderedDict
from typing import List, Optional, Tuple, Union

from .action import ActionArgsPack, ActionExecutor, ArgumentValue
from .path import NodePath


class Command:
    """Represents single command line typed in the shell"""

    def __init__(self, command_name):
        self.target = None
        self.name = command_name
        self.arguments = []

    def __str__(self):
        representation = " ".join(map(Command._to_string, [self.name] + self.arguments))
        if self.target is None:
            return representation
        representation = "{}: {}".format(Command._to_string(self.target), representation)
        return representation

    @staticmethod
    def _to_string(param):
        if isinstance(param, Command):
            return "{{{}}}".format(str(param))
        return str(param)


class CommandInterpreter:
    """Actually executes commands on provided backend tree"""

    def __init__(self, tree: ActionExecutor) -> None:
        self.tree = tree

    def execute(self, command: Command):
        if command is None:
            raise ValueError("No command to execute provided")
        target_path = self._evaluate(command.target)
        if target_path is None:
            raise RuntimeError("No action target specified")
        target_path = NodePath.cast(target_path)
        action_path = NodePath.cast(self._evaluate(command.name))
        arguments = list(map(self._evaluate, command.arguments))
        packed_arguments = parse_argument_tree(arguments)
        return self.tree.execute(target_path, action_path, packed_arguments)

    def _evaluate(self, part):
        if isinstance(part, Command):
            return self.execute(part)
        return part


def convert_token_type(token):
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token


def tokenize(text: str) -> List[str]:
    tokens = []
    tok = ""

    def finish_token():
        nonlocal tok, tokens
        if tok:
            tok = convert_token_type(tok)
            tokens.append(tok)
            tok = ""

    verbatim_mode = False
    verbatim_mode_finisher = None
    for char in text:
        if verbatim_mode:
            if char == verbatim_mode_finisher:
                finish_token()
                verbatim_mode = False
                verbatim_mode_finisher = None
            else:
                tok += char
        else:
            if char in "'\"":
                finish_token()
                verbatim_mode = True
                verbatim_mode_finisher = char
            elif char in "{}:#":
                finish_token()
                tokens.append(char)
            elif char.isspace():
                finish_token()
            else:
                tok += char
    finish_token()
    return tokens


class CommandParser:
    def __init__(self):
        self._root_scope = None

    def parse(self, command_line: str) -> Optional[Command]:
        tokens = tokenize(command_line)
        if not tokens:
            return None  # ignore empty lines
        if tokens[0] == "#":
            return None  # ignore comments

        self._root_scope = self._parse_scope(iter(tokens))
        return self._root_scope

    def _parse_scope(self, token_iterator) -> Command:
        parts = []
        for tok in token_iterator:
            if tok == "{":
                parts.append(self._parse_scope(token_iterator))
            elif tok != "}":
                parts.append(tok)
            else:
                break

        if ":" in parts:
            cmd = Command(parts[2])
            cmd.target = parts[0]
            cmd.arguments = parts[3:]
        else:
            cmd = Command(parts[0])
            cmd.arguments = parts[1:]
        return cmd


def parse_argument_tree(raw_arguments: List[str]) -> ActionArgsPack:
    pack_list: List[Tuple[Union[NodePath, int], ArgumentValue]] = []
    for i, arg in enumerate(raw_arguments):
        if isinstance(arg, str) and "=" in arg:
            key, value = arg.split("=")
            key_path = NodePath.from_python_name(key)
            if key_path.is_absolute:
                raise ValueError(f"Named argument path must be relative - {key_path}")
            typed_value = convert_token_type(value)
            pack_list.append((key_path, typed_value))
        else:
            pack_list.append((i, arg))
    return OrderedDict(pack_list)
