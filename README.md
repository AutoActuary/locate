# Locate

This library exposes three functions/callables
 - `this_dir()` returns the directory of the current Python file, or when using from an interactive session, it returns the current working directory.
 - `append_sys_path(relative_path)` allows importing from a location relative to the running Python file by resolving `relative_path` relative to `this_dir()` and appending it to `sys.path` (e.g. `relative_path="../foo/bar"`); note the functionality is also available as a context manager to allow temporary effect (e.g. `with append_sys_path("foo"): ...`).
 - `prepend_sys_path(relative_path)` is the same as `append_sys_path`, but prepending `sys.path` in order to be the first import location for Python to search for modules/files.
  

## Example use of this package
```
import locate

print(f"This file is located in: {locate.this_dir()}")

# Changing sys.path temporarily
with locate.prepend_sys_path("foo"):
    print(f"I can temporarily import from: {locate.this_dir().joinpath('foo')}")
print(f"I can no longer import from: {locate.this_dir().joinpath('foo')}")

# Changing sys.path permanently
locate.prepend_sys_path("foo")
print(f"I can now always import from: {locate.this_dir().joinpath('foo')}")

```

## Motivation
This package is for people who frequently use the directory of their scripts for storing files and custom modules and do not want their pipeline to break from an interactive shell. This is based on how Julia thinks about the immediate directory through its [@\_\_DIR\_\_](https://docs.julialang.org/en/v1/base/base/#Base.@__DIR__) macro.

`locate.this_dir()` is defined as:

 - When running a `.py` file, this is the file's base directory. 
 - When running an `.ipyn` notebook, this is the current working directory. This is the desired/expected result since Jupyter sets the working directory as the `.ipynb` base directory by default.
 - When running in a REPL, this is also the current working directory. This is similar to Julia's [@\_\_DIR\_\_](https://docs.julialang.org/en/v1/base/base/#Base.@__DIR__) macro.

## Other considerations
For a good discussion on retrieving the current Python path, see https://stackoverflow.com/questions/3718657
