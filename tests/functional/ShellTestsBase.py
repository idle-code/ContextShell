import unittest
from abc import ABC, abstractmethod

from contextshell.TreeRoot import TreeRoot
from contextshell.Shell import Shell
from contextshell.NodePath import NodePath
from contextshell.CommandInterpreter import CommandInterpreter
from contextshell.VirtualTree import VirtualTree
from contextshell.NodeTreeRoot import NodeTreeRoot


class ShellScriptTestsBase(unittest.TestCase, ABC):
    @abstractmethod
    def create_shell(self) -> Shell:
        raise NotImplementedError()


class TreeRootTestsBase(ShellScriptTestsBase):
    @abstractmethod
    def create_tree_root(self) -> TreeRoot:
        raise NotImplementedError()

    def create_shell(self):
        self.tree_root = self.create_tree_root()
        self.configure_tree_root(self.tree_root)

        interpreter = CommandInterpreter(self.tree_root)
        shell = Shell(interpreter)
        return shell

    def configure_tree_root(self, tree_root: TreeRoot):
        pass


# TODO: is this class needed when testing single TreeRoot-based class?
class VirtualTreeTestsBase(TreeRootTestsBase):
    def create_tree_root(self) -> TreeRoot:
        return VirtualTree()

    def configure_tree_root(self, tree_root: TreeRoot):
        self.configure_virtual_tree(tree_root)


    @abstractmethod
    def configure_virtual_tree(self, virtual_tree: VirtualTree):
        raise NotImplementedError()


class NodeTreeTestsBase(VirtualTreeTestsBase):  # TODO: move to NodeTree tests
    def configure_virtual_tree(self, virtual_tree: VirtualTree):
        tree_root = NodeTreeRoot()
        self.configure_node_tree(tree_root)
        virtual_tree.mount(NodePath("."), tree_root)

    def configure_node_tree(self, tree: NodeTreeRoot):
        pass
