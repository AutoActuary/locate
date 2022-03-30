import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="locate",
    version="1.1.0",
    author="Heetbeet",
    author_email="sfstreicher@gmail.com",
    description="Locate the file location of your current running script.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heetbeet/locate",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.4",
    install_requires=[],
)
