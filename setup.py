from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-code-docgen",
    version="0.2.0",
    author="ci-psy",
    author_email="icosmo2@gmail.com",
    description="Generate structured Markdown documentation from project directories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ci-psy/DocGen",
    packages=find_packages(),
    package_data={
        "py_code_docgen": ["*.py"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "dataclasses>=0.6; python_version < '3.7'"
    ],
    entry_points={
        'console_scripts': [
            'py-code-docgen=py_code_docgen.docgen:main',
        ],
    },
) 