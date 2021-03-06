import tempfile
import unittest
from pathlib import Path

from .bases import ActionTestsBase


def create_filesystem_tree(*args, **kwargs):
    from contextshell.backends.filesystem import FilesystemTree
    return FilesystemTree(*args, **kwargs)


class FilesystemActionsTestsBase(ActionTestsBase):
    """Test base for tests wishing to use actual filesystem directory"""
    def _make_test_path(self, relative_path):
        return Path(self.test_directory.name).joinpath(relative_path)

    def create_file(self, path: str, contents: str=None):
        full_path = self._make_test_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(contents if contents else '')

    def create_directory(self, path):
        full_path = self._make_test_path(path)
        full_path.mkdir(parents=True)

    def create_backend(self):
        return create_filesystem_tree(self.test_directory.name)

    def setUp(self):
        temp_dir_suffix = type(self).__name__
        self.test_directory = tempfile.TemporaryDirectory(temp_dir_suffix)

        super().setUp()

    def tearDown(self):
        self.test_directory.cleanup()
        super().tearDown()


class ContainsActionTests(FilesystemActionsTestsBase):
    def test_existing_file(self):
        self.create_file('file')

        exists = self.execute(".", "contains", 'file')

        self.assertTrue(exists)

    def test_existing_file_nested(self):
        self.create_file('parent/file')

        exists = self.execute(".", "contains", 'parent.file')

        self.assertTrue(exists)

    def test_existing_directory(self):
        self.create_directory('dir')

        exists = self.execute(".", "contains", 'dir')

        self.assertTrue(exists)

    def test_nonexistent(self):
        exists = self.execute(".", "contains", 'nonexistent')

        self.assertFalse(exists)

    def test_nonexistent_nested(self):
        self.create_directory('parent')

        exists = self.execute(".", "contains", 'parent.path')

        self.assertFalse(exists)


class GetActionTests(FilesystemActionsTestsBase):
    def test_empty_file(self):
        self.create_file('file')

        file_value = self.execute(".file", "get")

        self.assertEqual(file_value, '')

    def test_file(self):
        self.create_file('file', 'DATA')

        file_value = self.execute(".file", "get")

        self.assertEqual(file_value, 'DATA')

    def test_directory(self):
        self.create_directory('dir')

        dir_value = self.execute(".dir", "get")

        self.assertEqual(dir_value, None)


class IsActionTests(FilesystemActionsTestsBase):
    def test_directory_is_file(self):
        self.create_directory('dir')

        is_file = self.execute(".dir", "is.file")

        self.assertFalse(is_file)

    def test_file_is_file(self):
        self.create_file('file')

        is_file = self.execute(".file", "is.file")

        self.assertTrue(is_file)

    def test_directory_is_directory(self):
        self.create_directory('dir')

        is_dir = self.execute(".dir", "is.directory")

        self.assertTrue(is_dir)

    def test_file_is_directory(self):
        self.create_file('file')

        is_dir = self.execute(".file", "is.directory")

        self.assertFalse(is_dir)


class ListActionTests(FilesystemActionsTestsBase):
    def test_list_file(self):
        self.create_file('file')

        file_list = self.execute(".file", "list")

        self.assertEqual(file_list, [])

    def test_list_empty_directory(self):
        self.create_directory('dir')

        file_list = self.execute(".dir", "list")

        self.assertEqual(file_list, [])

    def test_list_directory_with_file_and_dirs(self):
        self.create_directory('parent/dir')
        self.create_file('parent/file')

        file_list = self.execute(".parent", "list")

        self.assertIn('dir', file_list)
        self.assertIn('file', file_list)

    @unittest.skip("Re-enable when path uses '/' as separator")
    def test_list_hidden(self):
        self.create_directory('parent/.dir')
        self.create_file('parent/.file')

        file_list = self.execute(".parent", "list")

        self.assertListEqual(file_list, [])

    @unittest.skip("Re-enable when path uses '/' as separator")
    def test_list_all(self):
        self.create_directory('parent/.dir')
        self.create_file('parent/.file')

        file_list = self.execute(".parent", "list.all")

        self.assertIn('@dir', file_list)
        self.assertIn('@file', file_list)


class ListActionsActionTests(FilesystemActionsTestsBase):
    def test_list_all(self):
        action_list = self.execute(".", "list.actions")

        self.assertSetEqual({'contains', 'get', 'is', 'list'}, set(action_list))

    def test_list_nested(self):
        action_list = self.execute(".", "list.actions", "is")

        self.assertSetEqual({'is.file', 'is.directory'}, set(action_list))
