r"""
Convenience functions for accessing the file path information of a script and allowing files to be imported
from the neighboring locations.

>>> import tempfile
>>> import subprocess
>>> import sys
>>> import shutil

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

Test relative imports using append_sys_path
>>> _ = tmpdir.joinpath('bar.py').open('w').write(f'''
... # Make sure "locate" is importable
... import sys
... import os
... sys.path.insert(0, os.path.abspath(r"{__file__}/.."))
... import locate
...
... locate.append_sys_path('..')
... import foo519efa14c17747dfb79fcbb766491c0b
... ''')
>>> subprocess.check_output([sys.executable, tmpdir.joinpath('bar.py')])
b''

Test relative imports using prepend_sys_path
>>> _ = tmpdir.joinpath('bar.py').open('w').write(f'''
... # Make sure "locate" is importable
... import sys
... import os
... sys.path.insert(0, os.path.abspath(r"{__file__}/.."))
... import locate
...
... locate.prepend_sys_path('..')
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
from typing import Union, Optional
import uuid
import warnings


class _StrWithAnID(str):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.unique_id = str(uuid.uuid4())


def _this_dir(stack):
    caller_info = stack[1]
    caller_globals = caller_info.frame.f_globals

    # Use os.path.abspath rather than Path.resolve, since Path.resolve will resolve symlinks to their sources
    if "__file__" in caller_globals:
        return Path(os.path.abspath(caller_globals["__file__"])).parent
    else:
        return Path(os.path.abspath(os.getcwd()))


def this_dir() -> Union[Path, None]:
    """
    This function mimics the @__DIR__ macro from Julia: https://docs.julialang.org/en/v1/base/file/#Base.@__DIR__
    Get a directory location associated with the caller of this function. If the caller is calling from a source
    code file, return the full path of the directory of that file, otherwise return the full path of the current
    working directory.
    """
    return _this_dir(inspect.stack())


class append_sys_path:
    """
    Resolve `relative_path` relative to the caller's directory path, and add it to sys.path. This will allow you to
    import files and modules directly from that directory. Note that previously defined import paths (such as the
    internal site-packages directory) will take importing preference; for inverse behaviour, use
    `prepend_sys_path`. This can be used as a context manager `with append_sys_path()` for temporary effect.
    """
    def __init__(
            self,
            relative_path: Union[str, Path] = '.'
    ) -> None:
        # Use os.path.abspath rather than Path.resolve, since Path.resolve will resolve symlinks to their sources
        self.added_path = _StrWithAnID(os.path.abspath(Path(_this_dir(inspect.stack()), relative_path)))
        sys.path.append(str(self.added_path))

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i in range(len(sys.path), -1, -1):
            if hasattr(sys.path[i], "unique_id") and getattr(sys.path[i], "unique_id") == self.added_path.unique_id:
                sys.path.pop(i)


class prepend_sys_path:
    """
    Resolve `relative_path` relative to the caller's directory path, and add it to sys.path. This will allow you to
    import files and modules directly from that directory. Note that this path takes preference over previously defined
    import paths (such as the internal site-packages directory); for inverse behaviour, use
    `append_sys_path`. This can be used as a context manager `with append_sys_path()` for temporary effect.
    """
    def __init__(
            self,
            relative_path: Union[str, Path] = '.'
    ) -> None:
        # Use os.path.abspath rather than Path.resolve, since Path.resolve will resolve symlinks to their sources
        self.added_path = _StrWithAnID(os.path.abspath(Path(_this_dir(inspect.stack()), relative_path)))
        sys.path.insert(0, str(self.added_path))

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i in range(len(sys.path)):
            if hasattr(sys.path[i], "uniqueid") and getattr(sys.path[i], "uniqueid") == self.added_path.unique_id:
                sys.path.pop(i)


def allow_relative_location_imports(relative_path: Union[str, Path] = '.') -> None:
    """
    Deprecated deprecated in favor of `append_sys_path`
    """
    warnings.warn(
        "`allow_relative_location_imports` is deprecated in favor of `append_sys_path` and will be removed locate "
        "4.0.0",
        category=DeprecationWarning
    )
    sys.path.append(os.path.abspath(Path(_this_dir(inspect.stack()), relative_path)))


def force_relative_location_imports(relative_path: Union[str, Path] = '.') -> None:
    """
    Deprecated in favor of `prepend_sys_path`
    """
    warnings.warn(
        "`force_relative_location_imports` is deprecated in favor of `prepend_sys_path` and will be removed in locate "
        "4.0.0",
        category=DeprecationWarning
    )
    sys.path.insert(0, os.path.abspath(Path(_this_dir(inspect.stack()), relative_path)))
