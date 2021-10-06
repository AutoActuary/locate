# Locate

This library exposes two functions `this_file()` and `this_dir()` in order to locate the file and directory path of your current running script.

## How to use this package
```
import locate
print("This file is:", locate.this_file())
print("This file is located in:", locate.this_dir())
```

## Motivation
I frequently use the directory of my scripts (for accessing files stored along side them), but I also frequently run these scripts in an interactive shell for debugging purposes. I therefore wanted something similar to Julia's [@\_\_DIR\_\_ macro](https://docs.julialang.org/en/v1/base/file/#Base.@__DIR__).

`locate.this_dir()` is defined as:

 - When running a `.py` file, this it the file's base directory. 
 - When running an `.ipyn` notebook, this is the current working directory. This is the desired/expected result, since Jupyter sets the working directory as the `.ipynb` base directory by default.
 - When running in a REPL, this is the current working directory. This is similar to Julia's `@__DIR__` macro https://docs.julialang.org/en/v1/base/file/#Base.@__DIR__

## Other considerations
For a good discussion on retrieving the current Python path, see https://stackoverflow.com/questions/3718657
