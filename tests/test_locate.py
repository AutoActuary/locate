import os
import subprocess
import sys
from pathlib import Path
import unittest

from locate import prepend_sys_path, append_sys_path, this_dir


class Tests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Remove the helper_scripts path from sys.path before testing.
        """
        i = len(sys.path) - 1
        while i >= 0:
            if Path(sys.path[0]).name == "helper_scripts":
                sys.path.pop(i)
            i -= 1

    def test_this_dir(self) -> None:
        self.assertEqual(this_dir().name, "tests")
        self.assertEqual(this_dir(), Path(os.path.abspath(__file__)).parent)

    def test_terminal_results(self) -> None:
        """
        Test if this_dir() evaluates to the same path as os.getcwd() when in interactive/terminal mode.
        """
        ret_bytes = subprocess.check_output(
            [
                sys.executable,
                "-c",
                "import sys;"
                "import os;"
                f'sys.path.insert(0, os.path.abspath(r"{__file__}/.."));'
                "from locate import this_dir;"
                "print(this_dir());"
                "print(os.getcwd());",
            ]
        )
        ret, retcwd = ret_bytes.decode("utf-8").strip().replace("\r", "").split("\n")
        self.assertEqual(ret.lower(), os.path.abspath(retcwd).lower())

    def test_import_from_helper_scripts_using_prepend_sys_path(self) -> None:
        """
        Test relative imports using prepend_sys_path.
        The relative path isn't available after using the function if
        the context manager functionality was used.
        """
        with self.assertRaises(ModuleNotFoundError):
            # noinspection PyUnresolvedReferences
            import foo_test_import__01  # type: ignore

        with prepend_sys_path("helper_scripts"):
            # noinspection PyUnresolvedReferences
            import foo_test_import__01

            self.assertEqual(foo_test_import__01.var, "test")

        with self.assertRaises(ModuleNotFoundError):
            # noinspection PyUnresolvedReferences
            import foo_test_import__02  # type: ignore

    def test_import_from_helper_scripts_using_append_sys_path(self) -> None:
        """
        Test relative imports using append_sys_path.
        The relative path isn't available after using the function if
        the context manager functionality was used.
        """
        with self.assertRaises(ModuleNotFoundError):
            # noinspection PyUnresolvedReferences
            import foo_test_import__03  # type: ignore

        with append_sys_path("helper_scripts"):
            # noinspection PyUnresolvedReferences
            import foo_test_import__03

            self.assertEqual(foo_test_import__03.var, "test")

        with self.assertRaises(ModuleNotFoundError):
            # noinspection PyUnresolvedReferences
            import foo_test_import__04  # type: ignore

    def test_function_prepend_sys_path(self) -> None:
        prepend_sys_path("helper_scripts")
        self.assertEqual(Path(sys.path[0]).name, "helper_scripts")

    def test_function_append_sys_path(self) -> None:
        append_sys_path("helper_scripts")
        self.assertEqual(Path(sys.path[-1]).name, "helper_scripts")


if __name__ == "__main__":
    unittest.main()
