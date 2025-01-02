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

- 🧙‍♂️ Interactive wizard mode for easy configuration
- 🌳 Project tree visualization with customizable filters
- 📚 Table of contents with multiple format options
- 🔍 Smart file filtering by extension
- 📊 Detailed file statistics and analytics
- ⚡ Fast project reports for quick insights
- 🎨 Syntax highlighting for multiple languages
- 📋 Optional line numbers in code blocks
- 🔗 Clickable navigation with customizable anchors
- 📦 Large file chunking for better performance
- 🎯 Minimal and full formatting options
- 🔄 CLI command generation for automation

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
> Remember to activate the virtual environment each time you work on the project. Your terminal prompt should change to `(venv) $` when it's active.

---

## Quick Start 🚀

### 1. Interactive Wizard (Recommended)
Start the interactive configuration wizard:
```bash
py-code-docgen -i
```

The wizard will:
- Offer to show a quick project overview
- Guide you through all configuration options
- Generate a CLI command for future use
- Preview settings before generating documentation

### 2. Fast Project Report
Get a quick overview of your project:
```bash
py-code-docgen --fast-report
```

### 3. Direct Command Line Usage
Generate documentation with specific options:
```bash
py-code-docgen [project_dir] -o output.md --include "py,js,cpp"
```

### 4. View All Options
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

### Key Options Explained
- `--include "ext1,ext2"`: Specify which file types to document
- `--show "ext1,ext2"`: Control which files appear in the tree view
- `--chunk-size N`: Split large files into N-line chunks for better readability
- `--toc-format`: Choose how files are displayed in the table of contents
- `--collapsible-level`: Control which sections can be collapsed

---

## Interactive Wizard Features

The `-i` flag launches an interactive wizard that helps you:

1. **Project Overview** 
   - Optional fast report before configuration
   - File type detection and statistics
   - Quick project insights

2. **Smart Configuration**
   - Step-by-step guided setup
   - File type filtering with auto-detection
   - Tree view customization
   - TOC format selection
   - Collapsible section control

3. **Output Customization**
   - Multiple documentation styles
   - Line number options
   - File information detail levels
   - Large file handling settings

4. **CLI Command Generation**
   - Generates equivalent command line
   - Perfect for automation or scripting
   - Easy to save and reuse settings

Example generated command:
```bash
py-code-docgen "my_project" -o "docs.md" --include "py,js" --toc-format full --collapsible-level main --line-numbers
```

---

## Examples

### Basic Documentation
```bash
py-code-docgen .
```

### Python-Only Documentation
```bash
py-code-docgen --include py --no-toc --minimal
```

### Detailed C++ Documentation
```bash
py-code-docgen --include cpp --toc-format full --collapsible-level main --line-numbers
```

### Quick Project Analysis
```bash
py-code-docgen --fast-report
```

### Large Project with Chunking
```bash
py-code-docgen . --chunk-size 100 --collapsible-level all
```

---

## Output Customization

### Table of Contents Formats
- **Full paths**: `dir/subdir/file.ext`  
- **Name with extension**: `file.ext`  
- **Just name**: `file`

### Collapsible Sections
- **All sections**: Everything collapsible
- **Main sections**: Only file sections collapsible
- **Subsections**: Only details collapsible
- **None**: Everything expanded

### File Information
- File sizes and line counts
- Last modified timestamps
- File type statistics
- Custom path information

### Code Display
- Syntax highlighting
- Optional line numbers
- Customizable chunk sizes
- Multiple formatting styles

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.