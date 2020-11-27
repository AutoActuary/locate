# Locate

This library locate the file location and directory path of your current running script.

## How to use this package
```
import locate
print("This file is:", locate.this_file())
print("This file is located in:", locate.this_file())
```

## Motivation
I frequently use the directory of my scripts (for accessing files stored along side them), but I also frequently run these scripts in an interactive shell for debugging purposes. I define `this_dir()` to retrun the following path:

 - When running a `.py` file, this it the file's base directory. 
 - When running an `.ipyn` notebook, this is the current working directory. This is always the correct, since Jupyter sets the working directory as the `.ipynb` base directory.
 - When running in a REPL, this is the current working directory. This is similar to Julia's `__DIR__` macro https://docs.julialang.org/en/v1/base/file/#Base.@__DIR__

## Other considerations
For a good discussion on retrieving the current Python path, see https://stackoverflow.com/questions/3718657
