# Locate

This library exposes three functions
 - `this_dir()` to locate the directory path of your current running script
 - `allow_relative_location_imports(x)` to allow importing files/modules relative to `this_dir()`; e.g. `.` or `../foo`
 - `force_relative_location_imports(x)` same as `allow_relative...` but with preference over internal directories; e.g. to overwrite an installed package

## Example use of this package
```
import locate

print(f"This file is located in: {locate.this_dir()}")

locate.allow_relative_location_imports("foo")
print(f"I can now import from: {locate.this_dir().joinpath('foo')}")
```

## Motivation
This package is for people who frequently use the directory of their scripts for storing files and custom modules, and don't want their pipeline to break from an interactive shell. This is based on the way Julia thinks about the immediate directory through its [@\_\_DIR\_\_ macro](https://docs.julialang.org/en/v1/base/file/#Base.@__DIR__).

`locate.this_dir()` is defined as:

 - When running a `.py` file, this is the file's base directory. 
 - When running an `.ipyn` notebook, this is the current working directory. This is the desired/expected result since Jupyter sets the working directory as the `.ipynb` base directory by default.
 - When running in a REPL, this is the current working directory. This is similar to Julia's `@__DIR__` macro https://docs.julialang.org/en/v1/base/file/#Base.@__DIR__

## Other considerations
For a good discussion on retrieving the current Python path, see https://stackoverflow.com/questions/3718657
