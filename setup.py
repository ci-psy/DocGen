from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-code-docgen",
    version="0.1.6",
    author="Cosmo Inclan",
    author_email="icosmo2@gmail.com", 
    description="A powerful documentation generator that creates beautiful markdown documentation from source code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ci-psy/DocGen",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "typing>=3.7.4.3",
        "dataclasses>=0.6; python_version < '3.7'",
        "pathlib>=1.0.1; python_version < '3.4'",
        "argparse>=1.4.0"
    ],
    entry_points={
        'console_scripts': [
            'py-code-docgen=docgen.docgen:main',
        ],
    },
) 