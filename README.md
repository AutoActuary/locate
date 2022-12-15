# Locate

This library provides three callables:

- `this_dir()` returns the directory of the current Python file, or when using from an interactive session, it returns
  the current working directory.
- `append_sys_path(relative_path)` allows importing from a location relative to the running Python file by
  resolving `relative_path` relative to `this_dir()` and appending it to `sys.path` (e.g. `relative_path="../foo/bar"`).
  This also works as a context manager to allow temporary effect (e.g. `with append_sys_path("foo"): ...`).
- `prepend_sys_path(relative_path)` is the same as `append_sys_path`, but prepending `sys.path` in order to be the first
  import location for Python to search rather than the last.

## Safety

The `*_sys_path` destructors (when exiting the with block) are safe from any side effect your package imports may have
on `sys.path`. It's not a naive implementation such as removing the first/last element or removing the element by value;
it employs a string subclass with an additional `id` property to keep tags of `sys.path` insertions. It is, therefore,
completely safe and allows for any further nesting of `with *_sys_path` within the import tree.

## Examples

### Input

```python
import locate
from pathlib import Path

this_dir = locate.this_dir()

print(f"This file is located in: {this_dir}")
print()

# Create files to demonstrate importing from a directory
foo = Path(locate.this_dir(), "foo")
foo.mkdir(exist_ok=True)

Path(foo, "bar1.py").write_text("print('Importing bar1')")
Path(foo, "bar2.py").write_text("print('Importing bar2')")
Path(foo, "bar3.py").write_text("print('Importing bar3')")
Path(foo, "bar4.py").write_text("print('Importing bar4')")

# Changing sys.path temporarily
with locate.prepend_sys_path("foo"):
    print(f"I can temporarily import from: {Path(this_dir, 'foo')}")
    import bar1

    print()

print(f"I can no longer import from: {Path(this_dir, 'foo')}")
try:
    import bar2
except ImportError:
    print("Cannot import bar2")
print()

# Changing sys.path permanently
locate.prepend_sys_path("foo")
print(f"I can now always import from: {Path(this_dir, 'foo')}")
import bar3
import bar4

print()
```

### Output

```
This file is located in: C:\Users\simon

I can temporarily import from: C:\Users\simon\foo
Importing bar1

I can no longer import from: C:\Users\simon\foo
Cannot import bar2

I can now always import from: C:\Users\simon\foo
Importing bar3
Importing bar4
```

## Motivation

This package is for people who frequently use the directory of their scripts for storing files and custom modules and do
not want their pipeline to break from an interactive shell. This is based on how Julia thinks about the immediate
directory through its [@\_\_DIR\_\_](https://docs.julialang.org/en/v1/base/base/#Base.@__DIR__) macro.

`locate.this_dir()` is defined as:

- When running a `.py` file, this is the file's base directory.
- When running an `.ipyn` notebook, this is the current working directory. This is the desired/expected result since
  Jupyter sets the working directory as the `.ipynb` base directory by default.
- When running in a REPL, this is also the current working directory. This is similar to
  Julia's [@\_\_DIR\_\_](https://docs.julialang.org/en/v1/base/base/#Base.@__DIR__) macro.

## Other considerations

For a good discussion on retrieving the current Python path, see https://stackoverflow.com/questions/3718657
