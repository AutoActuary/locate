import os
import subprocess
import sys
from pathlib import Path
import unittest

sys.path.insert(0, Path(__file__).resolve().parent)
import locate


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

    def test_this_dir(self):
        self.assertEqual(locate.this_dir().name, "tests")
        self.assertEqual(locate.this_dir(), Path(os.path.abspath(__file__)).parent)

    def test_terminal_results(self):
        """
        Test if this_dir() evaluates to the same path as os.getcwd() when in interactive/terminal mode.
        """
        ret = subprocess.check_output(
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
        ret, retcwd = ret.decode("utf-8").strip().replace("\r", "").split("\n")
        self.assertEqual(ret.lower(), os.path.abspath(retcwd).lower())

    def test_import_from_helper_scripts_using_prepend_sys_path(self):
        """
        Test relative imports using prepend_sys_path.
        The relative path isn't available after using the function if
        the context manager functionality was used.
        """
        with self.assertRaises(ModuleNotFoundError):
            import foo_test_import__01

        with locate.prepend_sys_path("helper_scripts"):
            import foo_test_import__01

            self.assertEqual(foo_test_import__01.var, "test")

        with self.assertRaises(ModuleNotFoundError):
            import foo_test_import__02

    def test_import_from_helper_scripts_using_append_sys_path(self):
        """
        Test relative imports using append_sys_path.
        The relative path isn't available after using the function if
        the context manager functionality was used.
        """
        with self.assertRaises(ModuleNotFoundError):
            import foo_test_import__03

        with locate.append_sys_path("helper_scripts"):
            import foo_test_import__03

            self.assertEqual(foo_test_import__03.var, "test")

        with self.assertRaises(ModuleNotFoundError):
            import foo_test_import__04

    def test_function_prepend_sys_path(self):
        locate.prepend_sys_path("helper_scripts")
        self.assertEqual(Path(sys.path[0]).name, "helper_scripts")

    def test_function_append_sys_path(self):
        locate.append_sys_path("helper_scripts")
        self.assertEqual(Path(sys.path[-1]).name, "helper_scripts")


if __name__ == "__main__":
    unittest.main()
