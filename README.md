# DocGen — Codebase Documentation Generator

DocGen scans your project directory and automatically generates comprehensive Markdown documentation. It creates:
- A visual directory tree of your codebase
- Code snippets with syntax highlighting
- File summaries and statistics
- A structured table of contents

You can target specific:
- Directories (e.g., only 'src/' and 'tests/')
- File types (e.g., only Python and JavaScript files)
- Code sections (using chunk size limits)
- Tree depth and visibility

[![PyPI version](https://img.shields.io/pypi/v/py-code-docgen.svg?x=0)](https://pypi.org/project/py-code-docgen/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Quick Start
```bash
# Install
pip install py-code-docgen

# Run interactive wizard
docgen -i

# Or generate docs directly
docgen . -o docs.md --include "py,js,cpp"

# Target specific folders and types
docgen . --folders "src,tests" --include "py" --show-progress
```

## Features
- 🧙‍♂️ Interactive wizard for easy configuration
- 🌳 Project structure visualization with file filtering
- 📝 Code blocks with language detection
- 🎨 Customizable output (minimal/detailed)
- 📊 File statistics and line counts
- ⚡ Fast report mode for quick overviews
- 🎯 Selective documentation of directories and file types

Perfect for:
- Project documentation
- Codebase exploration
- Technical documentation
- Code review preparation