r"""
Convenience functions for accessing the file path information of a script and allowing files to be imported
from the neighboring locations.

>>> import tempfile
>>> import subprocess
>>> import sys
>>> import shutil

Return this_dir.py as it's caller?
>>> _this_file() == Path(os.path.abspath(__file__))
True

>>> this_dir() == Path(os.path.abspath(__file__)).parent
True

Create a dummy file and test it's file path information
>>> tmpfile = Path(tempfile.mktemp(suffix='_foo.py'))
>>> fstr = rf'''
... # Make sure "locate" is importable
... import sys
... import os
... sys.path.insert(0, os.path.abspath(r"{__file__}/.."))
...
... # Use locate in this script
... import locate
... print(locate.this_dir())
... '''
>>> with open(tmpfile, 'w') as f:
...     _ = f.write(fstr)

>>> ret = subprocess.check_output([sys.executable, str(tmpfile)])
>>> sdir = ret.decode('utf-8').strip()

>>> str(sdir).lower() == str(tmpfile.resolve().parent).lower()
True

Test getting directory information from the REPL
>>> os.chdir(tempfile.gettempdir())
>>> ret = subprocess.check_output([
...     sys.executable, "-c",
...         'import sys;'
...         'import os;'
...         f'sys.path.insert(0, os.path.abspath(r"{__file__}/.."));'
...         'from locate import this_dir;'
...         'print(this_dir());'
...         'print(os.getcwd());'
... ])
>>> ret, retcwd = ret.decode('utf-8').strip().replace('\r','').split('\n')
>>> ret.lower() == os.path.abspath(retcwd).lower()
True

>>> ret.lower() == os.path.abspath(os.getcwd()).lower()
True

Test that relative import without add_relative_to_path throws an error
>>> tmpdir = Path(tempfile.mktemp()).joinpath('nest')
>>> os.makedirs(tmpdir)
>>> tmpdir.parent.joinpath('foo519efa14c17747dfb79fcbb766491c0b.py').touch()
>>> _ = tmpdir.joinpath('bar.py').open('w').write(f'''
... import foo519efa14c17747dfb79fcbb766491c0b
... ''')
>>> subprocess.check_output([sys.executable, tmpdir.joinpath('bar.py')], stderr=subprocess.DEVNULL) # doctest: +ELLIPSIS
Traceback (most recent call last):
...
subprocess.CalledProcessError: Command '['...python...', ...bar.py...]' returned non-zero exit status 1.

Test relative imports using allow_relative_location_imports
>>> _ = tmpdir.joinpath('bar.py').open('w').write(f'''
... # Make sure "locate" is importable
... import sys
... import os
... sys.path.insert(0, os.path.abspath(r"{__file__}/.."))
... import locate
...
... locate.allow_relative_location_imports('..')
... import foo519efa14c17747dfb79fcbb766491c0b
... ''')
>>> subprocess.check_output([sys.executable, tmpdir.joinpath('bar.py')])
b''

Test relative imports using force_relative_location_imports
>>> _ = tmpdir.joinpath('bar.py').open('w').write(f'''
... # Make sure "locate" is importable
... import sys
... import os
... sys.path.insert(0, os.path.abspath(r"{__file__}/.."))
... import locate
...
... locate.force_relative_location_imports('..')
... import foo519efa14c17747dfb79fcbb766491c0b
... ''')
>>> subprocess.check_output([sys.executable, tmpdir.joinpath('bar.py')])
b''


>>> os.unlink(tmpfile)
>>> shutil.rmtree(tmpdir)
"""

import inspect
import os
import sys
from pathlib import Path
from typing import Union


def _file_path_from_stack_frame(stack_frame: inspect.FrameInfo.frame) -> Union[Path, None]:
    """
    Helper function to get the file location of a stack frame

    """
    caller_globals = stack_frame.f_globals

    if "__file__" in caller_globals:
        # Don't use Path.resolve, it will resolve to a symlink's true location, which is not a good definition
        # of what the caller's filepath is.
        return Path(os.path.abspath(caller_globals["__file__"]))
    else:
        return None


def _this_file() -> Union[Path, None]:
    """
    Get the full path of the caller's source code file location. If the caller is not calling from a source code file,
    such as calling from the REPL, return None.

    """
    stack = inspect.stack()
    caller_info = stack[1]

    return _file_path_from_stack_frame(caller_info.frame)


def this_dir() -> Union[Path, None]:
    """
    This function mimics the @__DIR__ macro from Julia: https://docs.julialang.org/en/v1/base/file/#Base.@__DIR__
    Get a directory location associated with the caller of this function. If the caller is calling from a source
    code file, return the full path of the directory of that file, otherwise return the full path of the current
    working directory.

    """
    stack = inspect.stack()
    caller_info = stack[1]
    filepath = _file_path_from_stack_frame(caller_info.frame)

    if filepath is None:
        return Path(os.path.abspath(os.getcwd()))
    else:
        return filepath.parent


def allow_relative_location_imports(relative_path: Union[str, Path] = '.') -> None:
    """
    Resolve `relative_path` relative to the caller's directory path, and add it to sys.path. This will allow you to
    import files and modules directly from that directory. Note that previously defined import paths (such as the
    internal site-packages directory) will take importing preference; for inverse behaviour, use
    `force_relative_location_imports`.

    """
    # Same logic than this_dir, but cannot call that function without messing up the stack frame
    stack = inspect.stack()
    caller_info = stack[1]
    filepath = _file_path_from_stack_frame(caller_info.frame)

    if filepath is None:
        dir_path = Path(os.path.abspath(os.getcwd()))
    else:
        dir_path = filepath.parent

    path_to_add = dir_path.joinpath(relative_path).resolve()
    if path_to_add not in sys.path:
        sys.path.append(str(path_to_add))


def force_relative_location_imports(relative_path: Union[str, Path] = '.') -> None:
    """
    Resolve `relative_path` relative to the caller's directory path, and add it to sys.path. This will allow you to
    import files and modules directly from that directory. Note that this path takes preference over previously defined
    import paths (such as the internal site-packages directory); for inverse behaviour, use
    allow_relative_location_imports.

    """
    # Same logic than this_dir, but cannot call that function without messing up the stack frame
    stack = inspect.stack()
    caller_info = stack[1]
    filepath = _file_path_from_stack_frame(caller_info.frame)

    if filepath is None:
        dir_path = Path(os.path.abspath(os.getcwd()))
    else:
        dir_path = filepath.parent

    path_to_add = dir_path.joinpath(relative_path).resolve()
    if path_to_add not in sys.path:
        sys.path.insert(0, str(path_to_add))
