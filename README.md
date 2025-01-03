# DocGen — Beautiful Documentation Generator 📚

Effortlessly generate Markdown documentation from your source code with DocGen.  
It’s quick to set up, highly configurable, and supports multiple languages.

[![PyPI version](https://badge.fury.io/py/py-code-docgen.svg?cache=bust)](https://badge.fury.io/py/py-code-docgen)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Table of Contents
1. [📋 Overview](#1-overview)
2. [✨ Features](#2-features)
3. [📦 Requirements](#3-requirements)
4. [⚡ Installation](#4-installation)
5. [🚀 Quick Start](#5-quick-start)
6. [💻 Command Line Options](#6-command-line-options)
7. [🧙‍♂️ Interactive Wizard](#7-interactive-wizard)
8. [📝 Examples](#8-examples)
9. [🎨 Output Customization](#9-output-customization)
10. [🔤 Supported Languages](#10-supported-languages)
11. [⚙️ Configuration](#11-configuration)
12. [🔧 Troubleshooting](#12-troubleshooting)
13. [👥 Contributing](#13-contributing)
14. [📄 License](#14-license)

---

## 1. Overview

DocGen makes it easy to create sleek, up-to-date project documentation.  
Use the **interactive wizard** for a guided setup or jump straight into the **CLI** for customized reports.

**Key benefits**:  
- Saves time with automatic scanning of files and folders  
- Offers multiple table of contents formats and collapsible sections  
- Handles large files by chunking content for better readability  
- Works on Windows, macOS, and Linux  

---

## 2. Features

- **Interactive Wizard**: Step-by-step prompts for quick config  
- **Project Tree Visualization**: Easily see project structure with file extension filters  
- **Selective Coverage**: Document subfolders or specific file types  
- **Flexible TOC**: Multiple formats (full paths, filenames, or minimal)  
- **Language-Aware**: Syntax highlighting and optional line numbers  
- **Chunking**: Read large files in manageable blocks  
- **Fast Reports**: Skip detail for high-level project stats (`--fast-report`)  
- **Automation**: Generate CLI commands for reuse  
- **Minimal or Full Output**: Choose a light or detailed style  
- **Progress Bar**: Visual feedback while scanning large projects  

---

## 3. Requirements

- **Python** 3.7+  
- Runs on Windows, macOS, Linux  

**Dependencies**:
- Standard Python libraries (`pathlib`, `typing`)
- `dataclasses` (only for Python < 3.7)

---

## 4. Installation

### Simple (Global)
```bash
pip install py-code-docgen
```

### Development (Recommended)
```bash
git clone https://github.com/ci-psy/DocGen.git
cd DocGen
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate.bat # Windows
pip install -r requirements.txt
```

---

## 5. Quick Start

1. **Interactive Wizard**  
   ```bash
   py-code-docgen -i
   ```
2. **Fast Report**  
   ```bash
   py-code-docgen --fast-report
   ```
3. **Basic Usage**  
   ```bash
   py-code-docgen [project_dir] -o output.md --include "py,js,cpp"
   ```
4. **Help**  
   ```bash
   py-code-docgen --help
   ```

---

## 6. Command Line Options

```bash
usage: py-code-docgen [options] [project_dir]
```

- `--include "ext1,ext2"`: Only document these file extensions  
- `--folders "folder1,folder2"`: Restrict documentation to specific subfolders  
- `--show "ext1,ext2"`: Control which extensions appear in the project tree  
- `--chunk-size N`: Break large files into chunks of size N lines  
- `--toc-format`: Set how the table of contents labels files  
- `--collapsible-level`: Choose sections to make collapsible  
- `--show-progress`: Enable a progress bar  

More details are available with:  
```bash
py-code-docgen --help
```

---

## 7. Interactive Wizard

The wizard guides you through:  
- **Project Overview**: Basic stats and file listing  
- **File Types and Subfolders**: Select which files to include  
- **TOC and Collapsible Sections**: Decide how sections appear  
- **CLI Command Generation**: Easily reuse or share the exact command

Example wizard command:  
```bash
py-code-docgen "my_project" -o "docs.md" \
  --include "py,js" --toc-format full \
  --collapsible-level main --line-numbers
```

---

## 8. Examples

- **Basic**  
  ```bash
  py-code-docgen .
  ```
- **Python Only**  
  ```bash
  py-code-docgen --include py --no-toc --minimal
  ```
- **C++ + Collapsible**  
  ```bash
  py-code-docgen --include cpp --toc-format full \
    --collapsible-level main --line-numbers
  ```
- **Fast Analysis**  
  ```bash
  py-code-docgen --fast-report
  ```
- **Chunking Large Files**  
  ```bash
  py-code-docgen . --chunk-size 100 --collapsible-level all
  ```
- **Subfolders**  
  ```bash
  py-code-docgen . --folders "src,tests" --include "py" --show-progress
  ```

---

## 9. Output Customization

- **TOC Format**: Full paths, filename.ext, or just the name  
- **Collapsible Sections**: Adjust the collapsible level (all, main only, or none)  
- **File Info**: Include file size, timestamps, and line counts  
- **Code Display**: Syntax highlighting, line numbers, chunking  

---

## 10. Supported Languages

DocGen supports a wide range of languages, including but not limited to:

- **Web/Markup**: `.html`, `.css`, `.jsx`, `.tsx`, `.vue`, `.scss`, `.less`  
- **Python**: `.py`, `.pyi`, `.pyx`, `.pxd`  
- **C/C++**: `.c`, `.cpp`, `.cc`, `.cxx`, `.hpp`, etc.  
- **Java/JVM**: `.java`, `.kt`, `.kts`, `.groovy`, `.scala`  
- **Shell**: `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`  
- **Other**: Swift, Rust, Go, PHP, Ruby, Lua, Dart, etc.

**Note**: Syntax highlighting depends on your Markdown viewer.

---

## 11. Configuration

- **Exclude Patterns**: `--exclude "node_modules/,*.test.js"`  
- **Subfolders Only**: `--folders "src,tests"`  
- **Chunk Size**: `--chunk-size 100`  

**Minimal Mode**:
```bash
py-code-docgen --minimal
```
**Full Mode**:
```bash
py-code-docgen --show-all --line-numbers --path-info
```
**Progress Bar**:
```bash
py-code-docgen --show-progress
```

---

## 12. Troubleshooting

- **Command Not Found**: Make sure you’ve activated the virtual environment or installed globally  
- **Large Files**: Lower the `--chunk-size`  
- **Encoding Errors**: Check files are in UTF-8  
- **Permissions**: Verify you have the right access level  

Check version:
```bash
py-code-docgen --version
```

---

## 13. Contributing

Contributions are welcome! Please open issues or submit pull requests on GitHub.

---

## 14. License

This project is licensed under the [MIT License](LICENSE).