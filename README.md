# DocGen - Beautiful Documentation Generator

A powerful documentation generator that creates beautiful Markdown documentation from source code.

[![PyPI version](https://badge.fury.io/py/py-code-docgen.svg)](https://badge.fury.io/py/py-code-docgen)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Command Line Options](#command-line-options)
6. [Interactive Wizard Features](#interactive-wizard-features)
7. [Examples](#examples)
8. [Output Customization](#output-customization)
9. [Contributing](#contributing)
10. [License](#license)

---

## Features ✨

- Interactive wizard mode for easy configuration  
- Project tree visualization  
- Table of contents with customizable formats  
- Collapsible sections for better organization  
- File statistics and line counts  
- Fast project reports  
- Syntax highlighting for multiple languages  
- Line numbers in code blocks  
- Clickable navigation links  
- Customizable output formats  
- CLI command generation for repeatable documentation

---

## Requirements

- Python 3.7 or higher  
- Works on Windows, macOS, and Linux  

---

## Installation

### Option 1: Simple Installation (Global)
Install directly from PyPI:
```bash
pip install py-code-docgen
```

### Option 2: Development Installation (Recommended)
For development or when using a virtual environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/ci-psy/DocGen.git
   cd docgen
   ```

2. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate on macOS/Linux
   source venv/bin/activate

   # Activate on Windows (cmd.exe)
   venv\Scripts\activate.bat

   # Activate on Windows (PowerShell)
   venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

> **Note**  
> Remember to activate the virtual environment each time you work on the project. Your terminal prompt should change to `(venv) $` when it’s active.

---

## Quick Start 🚀

1. **Interactive Wizard Mode (Recommended)**:
   ```bash
   py-code-docgen -i
   ```

2. **Command Line Usage**:
   ```bash
   py-code-docgen [project_dir] -o output.md --include "py,js,cpp"
   ```

3. **View Help and Options**:
   ```bash
   py-code-docgen --help
   ```

---

## Command Line Options

```text
usage: py-code-docgen [-h] [-i] [--fast-report] [-o OUTPUT] [--include INCLUDE]
                      [--show SHOW] [--show-all] [--no-collapsible]
                      [--collapsible-level {all,main,subsections,none}]
                      [--minimal] [--line-numbers] [--no-summary] [--no-tree]
                      [--no-file-info] [--no-line-count] [--no-file-stats]
                      [--no-timestamps] [--no-sizes] [--no-toc]
                      [--toc-format {full,name_ext,name}] [--no-toc-anchors]
                      [--toc-anchor-style {simple,full_path}] [--path-info]
                      [--chunk-size CHUNK_SIZE]
                      [project_dir]
```

---

## Interactive Wizard Features

Using the `-i` flag guides you through setup:

1. **Optional Fast Report**: Get a quick project overview.  
2. **Step-by-Step Configuration**: Choose your documentation options interactively.  
3. **CLI Command Generation**: Save or share the automatically generated command.

Example:
```bash
py-code-docgen "my_project" -o "docs.md" --include "py,js" --toc-format full --collapsible-level main --line-numbers
```

---

## Examples

- **Generate documentation with default settings**:
  ```bash
  py-code-docgen .
  ```

- **Generate minimal documentation for Python files**:
  ```bash
  py-code-docgen --include py --no-toc --minimal
  ```

- **Generate documentation with full paths and main section collapsing**:
  ```bash
  py-code-docgen --include cpp --toc-format full --collapsible-level main
  ```

- **Generate a quick project report**:
  ```bash
  py-code-docgen --fast-report
  ```

---

## Output Customization

### TOC Formats
- **Full paths**: `dir/subdir/file.ext`  
- **Name with extension**: `file.ext`  
- **Just name**: `file`

### Collapsible Sections
- **All sections**  
- **Main sections only**  
- **Subsections only**  
- **None** (disabled)

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.