import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="locate",
    author="Heetbeet",
    author_email="sfstreicher@gmail.com",
    description="Locate the file location of your current running script.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AutoActuary/locate",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.4",
    use_scm_version={
        "write_to": "locate/version.py",
    },
    setup_requires=[
        "setuptools_scm",
    ],
    install_requires=[],
    package_data={
        "": [
            "py.typed",
        ],
    },
)
