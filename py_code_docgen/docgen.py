#!/usr/bin/env python3
"""
docgen.py
---------
Generates Markdown documentation from a project directory, including optional
tree diagrams, file summaries, code snippets, and more.

Features:
- Interactive wizard or direct CLI usage
- Project tree visualization with extension filtering
- Summaries and stats (line counts, file sizes, timestamps)
- Collapsible sections in Markdown
- Progress bar
- Minimal vs. normal formatting

Author: <ci-psy>
Version: 0.2.0
"""

import os
import datetime
import sys
import argparse
import time
from pathlib import Path
from typing import Set, List, Dict, Optional, NamedTuple, Callable, Tuple
from dataclasses import dataclass
import re

# ---------- ANSI Colors and Helpers ----------
COLORS = {
    "GREEN": "\033[92m",
    "CYAN": "\033[96m",
    "YELLOW": "\033[93m",
    "MAGENTA": "\033[95m",
    "BOLD": "\033[1m",
    "RESET": "\033[0m",
    "RED": "\033[91m",
    "BLUE": "\033[94m"
}

def color_msg(msg: str, color: str) -> str:
    """Wrap a string in the specified ANSI color code."""
    return f"{COLORS[color]}{msg}{COLORS['RESET']}"

__version__ = "0.2.3"


# ---------- Messaging (Info, Warnings, Errors) ----------

def _warn_user(msg: str) -> None:
    """Print a warning in yellow."""
    print(color_msg("Warning:", "YELLOW"), msg)

def _error_user(msg: str) -> None:
    """Print an error in red."""
    print(color_msg("Error:", "RED"), msg)

def _info_user(msg: str) -> None:
    """Print a neutral info message (no special color)."""
    print(msg)


# ---------- Helper Formatting ----------

def format_seconds(seconds: float) -> str:
    """Convert a float in seconds to [HH:MM:SS]."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_bar_chars() -> Tuple[str, str, str, str]:
    """Return Unicode chars for a progress bar."""
    return "█", "░", "|", "|"

def draw_progress_bar(
    current: int,
    total: int,
    start_time: float,
    bar_len: int = 30
) -> str:
    """
    Generate a simple progress bar with percentage, speed, and time estimates.
    Example:
      35%|██████░░░░░░░░░| 35/100 [00:03<00:05, 12.00 it/s]
    """
    fill_char, empty_char, left_bracket, right_bracket = get_bar_chars()
    elapsed = time.time() - start_time
    pct = current / total if total > 0 else 0.0
    filled = int(round(bar_len * pct))
    rate = current / elapsed if elapsed > 0 else 0.0

    elapsed_str = format_seconds(elapsed)
    remaining = (total - current) / rate if rate and current < total else 0
    remaining_str = format_seconds(remaining)

    bar_str = fill_char * filled + empty_char * (bar_len - filled)
    bar_colored = color_msg(bar_str, "CYAN")

    return (
        f"{int(pct * 100):3d}%{left_bracket}{bar_colored}{right_bracket} "
        f"{current}/{total} "
        f"[{elapsed_str}<{remaining_str}, {rate:5.2f} it/s]"
    )

def format_size(size: int) -> str:
    """Convert byte size to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def format_time(ts: float) -> str:
    """Format a UNIX timestamp as a human-readable datetime."""
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def add_line_numbers(code: str, start_line: int = 1) -> str:
    """Prefix each line with a line number."""
    lines = code.splitlines()
    width = len(str(start_line + len(lines) - 1))
    return "\n".join(f"{(i + start_line):{width}} │ {l}"
                     for i, l in enumerate(lines))

def make_anchor_id(raw: str) -> str:
    """Convert a string to a Markdown-safe anchor ID."""
    cleaned = re.sub(r'[^a-zA-Z0-9_-]+', '-', raw.strip().lower())
    return cleaned.strip('-')


# ---------- Data Structures ----------

class DocumentationOptions(NamedTuple):
    """User preferences for doc generation."""
    project_dir: str
    output_file: str
    include_extensions: str
    show_extensions: str
    show_all: bool
    show_file_info: bool
    show_tree: bool
    show_line_count: bool
    show_file_stats: bool
    show_timestamps: bool
    show_sizes: bool
    show_summary: bool
    use_collapsible: bool
    collapsible_level: str
    use_minimal_format: bool
    show_line_numbers: bool
    show_toc: bool
    toc_format: str
    use_toc_anchors: bool
    toc_anchor_style: str
    show_path_info: bool
    chunk_size: int
    show_progress: bool
    selected_folders: Optional[List[str]] = None

@dataclass
class FileInfo:
    """Metadata for a single file."""
    path: str
    size: int
    last_modified: float
    line_count: Optional[int] = None


# ---------- File and Folder Analysis ----------

class FileCache:
    """Optional cache for storing file stats and line counts."""
    def __init__(self) -> None:
        self._cache: Dict[str, FileInfo] = {}

    def get(self, path: str) -> Optional[FileInfo]:
        return self._cache.get(os.path.abspath(path))

    def set(self, path: str, info: FileInfo) -> None:
        self._cache[os.path.abspath(path)] = info

class ProjectAnalyzer:
    """
    Analyzes a project folder, tracking extension counts and line totals for text files.
    """
    TEXT_EXTENSIONS = {
        '.txt', '.md', '.swift', '.metal', '.py', '.js', '.html',
        '.css', '.json', '.xml', '.yaml', '.yml', '.cpp', '.h',
        '.c', '.ts'
    }

    def __init__(self, project_dir: str, file_cache: Optional[FileCache] = None) -> None:
        self.project_dir = os.path.abspath(project_dir)
        self.file_cache = file_cache or FileCache()
        self.stats: Dict[str, int] = {}
        self.total_lines = 0
        self.file_count = 0

    def is_text_file(self, file_path: str) -> bool:
        """Check if a file extension is recognized as text."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.TEXT_EXTENSIONS

    def analyze_project(self) -> Dict[str, int]:
        """Walk the dir, gather extension frequencies, track line counts if text."""
        for root, _, files in os.walk(self.project_dir):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                self.stats[ext] = self.stats.get(ext, 0) + 1
                self.file_count += 1

                full_path = os.path.join(root, fname)
                if self.is_text_file(full_path):
                    self.get_file_info(full_path)
        return self.stats

    def get_file_info(self, file_path: str) -> FileInfo:
        """
        Retrieve file info (including line count if text).
        Uses a cache to avoid repeated disk reads.
        """
        cached = self.file_cache.get(file_path)
        if cached:
            return cached

        p = Path(file_path)
        try:
            st = p.stat()
            fi = FileInfo(path=str(p), size=st.st_size, last_modified=st.st_mtime)
        except FileNotFoundError:
            fi = FileInfo(str(p), 0, 0)

        if self.is_text_file(str(p)):
            try:
                with open(p, 'r', encoding='utf-8') as fp:
                    lines = fp.readlines()
                    fi.line_count = len(lines)
                    self.total_lines += len(lines)
            except (OSError, UnicodeDecodeError):
                fi.line_count = 0

        self.file_cache.set(file_path, fi)
        return fi


# ---------- Parsing and Filtering ----------

def parse_extensions(ext_string: str) -> Set[str]:
    """
    Parse a comma-separated list of extensions.
    Returns an empty set if 'all' or '*' are specified (meaning 'include everything').
    """
    if not ext_string:
        return set()
    if ext_string.lower() in ["all", "*"]:
        return set()
    parts = [x.strip() for x in ext_string.split(',')]
    return {'.' + p.lstrip('.') for p in parts}

def parse_folders(folder_string: Optional[str], project_dir: str) -> Optional[List[str]]:
    """
    Convert user input to absolute folder paths under project_dir.
    Skips invalid or out-of-dir paths; merges overlapping paths.
    """
    if not folder_string:
        return None

    raw_folders = [f.strip() for f in folder_string.split(',') if f.strip()]
    abs_folders: List[str] = []

    for folder in raw_folders:
        candidate = folder if os.path.isabs(folder) else os.path.join(project_dir, folder)
        cand_abs = os.path.abspath(candidate)
        if not os.path.isdir(cand_abs):
            _warn_user(f"Skipping invalid folder: '{folder}'")
            continue

        proj_abs = os.path.abspath(project_dir)
        if not cand_abs.startswith(proj_abs + os.sep) and cand_abs != proj_abs:
            _warn_user(f"Skipping folder outside project directory: '{folder}'")
            continue
        abs_folders.append(cand_abs)

    # Remove duplicates and keep parent directories over children.
    abs_folders = list(set(abs_folders))
    abs_folders.sort(key=len)
    filtered: List[str] = []
    for folder in abs_folders:
        if not any(folder.startswith(p + os.sep) for p in filtered):
            filtered.append(folder)

    if not filtered:
        _warn_user("No valid subfolders recognized. Using full directory.")
        return None

    return filtered

def is_in_selected_folders(file_path: str, selected_folders: Optional[List[str]]) -> bool:
    """True if file_path is within one of the selected folders (if any)."""
    if not selected_folders:
        return True
    abs_path = os.path.abspath(file_path)
    return any(abs_path.startswith(sf + os.sep) or abs_path == sf for sf in selected_folders)

def is_ancestor_of_selected_folders(dir_path: str, selected_folders: Optional[List[str]]) -> bool:
    """True if dir_path is an ancestor of any selected folder."""
    if not selected_folders:
        return True
    abs_dir = os.path.abspath(dir_path)
    return any(sf.startswith(abs_dir + os.sep) for sf in selected_folders)

def get_yes_no_input(prompt: str, default: bool = True) -> bool:
    """
    Prompt for yes/no with a default choice.
    e.g.: get_yes_no_input("Continue?", True) -> [Y/n]
    """
    default_str = "Y/n" if default else "y/N"
    sys.stdout.write(f"{prompt} [{default_str}]: ")
    sys.stdout.flush()
    resp = sys.stdin.readline().strip().lower()
    if not resp:
        return default
    return resp[0] == 'y'

def include_file_in_doc(filename: str, include_extensions: Set[str]) -> bool:
    """Check if file matches extension filters (empty set => include all)."""
    if not include_extensions:
        return True
    return any(filename.endswith(ext) for ext in include_extensions)

def chunked_file_reader(file_path: str, chunk_size: int = 200) -> List[str]:
    """Read file in chunk_size lines per block."""
    chunks: List[str] = []
    buffer: List[str] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as fp:
            for line in fp:
                buffer.append(line)
                if len(buffer) >= chunk_size:
                    chunks.append(''.join(buffer))
                    buffer = []
        if buffer:
            chunks.append(''.join(buffer))
    except (OSError, UnicodeDecodeError):
        pass
    return chunks

def filter_project_entries(
    entries: List[Path],
    show_extensions: Optional[Set[str]],
    selected_folders: Optional[List[str]],
    ignore_hidden: bool = True
) -> List[Path]:
    """
    Filter out hidden items if requested, and keep only:
      - files matching show_extensions
      - directories relevant to the user selection or containing matching files
    """
    filtered = []
    for entry in entries:
        if ignore_hidden and entry.name.startswith('.'):
            continue
        if entry.is_file():
            if show_extensions and len(show_extensions) > 0:
                if any(entry.name.endswith(ext) for ext in show_extensions):
                    if is_in_selected_folders(str(entry), selected_folders):
                        filtered.append(entry)
            else:
                if is_in_selected_folders(str(entry), selected_folders):
                    filtered.append(entry)
        else:
            # Directory
            if is_in_selected_folders(str(entry), selected_folders) or \
               is_ancestor_of_selected_folders(str(entry), selected_folders):
                if show_extensions and len(show_extensions) > 0:
                    match_found = False
                    for root, _, fs in os.walk(entry):
                        if not (is_in_selected_folders(root, selected_folders) or
                                is_ancestor_of_selected_folders(root, selected_folders)):
                            continue
                        if any(fname.endswith(tuple(show_extensions)) for fname in fs):
                            match_found = True
                            break
                    if match_found:
                        filtered.append(entry)
                else:
                    filtered.append(entry)
    return filtered

def generate_tree(
    directory: str,
    show_extensions: Optional[Set[str]] = None,
    selected_folders: Optional[List[str]] = None,
    prefix: str = "",
    is_last: bool = True,
    ignore_hidden: bool = True
) -> List[str]:
    """
    Recursively generate a tree view of `directory`, applying filters.
    Returns a list of lines to print/write.
    """
    output: List[str] = []
    path_dir = Path(directory)

    if selected_folders:
        if not (is_in_selected_folders(str(path_dir), selected_folders) or 
                is_ancestor_of_selected_folders(str(path_dir), selected_folders)):
            return output

    try:
        entries = list(path_dir.iterdir())
    except PermissionError:
        return output

    entries = filter_project_entries(entries, show_extensions, selected_folders, ignore_hidden)
    entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

    for idx, entry in enumerate(entries):
        is_last_item = (idx == len(entries) - 1)
        branch = "└── " if is_last_item else "├── "
        current_prefix = prefix + branch

        if entry.is_dir():
            output.append(f"{current_prefix}{entry.name}/")
            deeper_prefix = prefix + ("    " if is_last_item else "│   ")
            output.extend(
                generate_tree(
                    str(entry),
                    show_extensions,
                    selected_folders,
                    deeper_prefix,
                    is_last_item,
                    ignore_hidden
                )
            )
        else:
            output.append(f"{current_prefix}{entry.name}")

    return output

def collect_files_in_tree_order(
    directory: str,
    in_tree_files: List[str],
    show_extensions: Optional[Set[str]],
    selected_folders: Optional[List[str]],
    include_extensions: Set[str],
    ignore_hidden: bool = True
) -> None:
    """
    Recursively walk `directory` in the same order as generate_tree,
    appending files to in_tree_files if they match extension & folder filters.
    """
    dir_path = Path(directory)

    if not is_in_selected_folders(str(dir_path), selected_folders) \
       and not is_ancestor_of_selected_folders(str(dir_path), selected_folders):
        return

    try:
        entries = list(dir_path.iterdir())
    except PermissionError:
        return

    entries = filter_project_entries(entries, show_extensions, selected_folders, ignore_hidden)
    entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

    for entry in entries:
        if entry.is_dir():
            collect_files_in_tree_order(
                str(entry),
                in_tree_files,
                show_extensions,
                selected_folders,
                include_extensions,
                ignore_hidden
            )
        else:
            if include_file_in_doc(entry.name, include_extensions) \
               and is_in_selected_folders(str(entry), selected_folders):
                in_tree_files.append(str(entry))


# ---------- Fast Report ----------

def print_fast_report(project_dir: str) -> None:
    """Print a quick summary of folder counts, file counts, and file extensions."""
    proj = ProjectAnalyzer(project_dir)
    proj.analyze_project()

    folder_count = 0
    for _, dirs, _ in os.walk(project_dir):
        folder_count += len(dirs)

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(color_msg(f"\nQuick Report: {project_dir}", "CYAN"))
    print(f"Generated on: {now}")
    print(f"Directory: {project_dir}")
    print(f"Total Folders: {folder_count}")
    print(f"Total Files: {proj.file_count}")
    print(f"Total Lines (approx): {proj.total_lines}")
    print("\nExtension Distribution:")
    for ext, count in sorted(proj.stats.items()):
        print(f"  {ext or '(no extension)'}: {count}")
    print()


# ---------- Writing Sections ----------

def write_top_level_doc_heading(file_obj, project_name: str, options: DocumentationOptions) -> None:
    """Write the top-level heading. Minimal mode uses plain text, else Markdown H1."""
    if options.use_minimal_format:
        file_obj.write(f"{project_name} Documentation\n\n")
    else:
        file_obj.write(f"# {project_name} Documentation\n\n")

def write_main_heading(file_obj, heading_text: str, anchor: Optional[str], options: DocumentationOptions) -> None:
    """
    Write a main heading for a file in normal or minimal style.
    If anchor is provided and use_toc_anchors=True, place an HTML anchor.
    """
    if options.use_minimal_format:
        if anchor and options.use_toc_anchors:
            file_obj.write(f'\n<span id="{anchor}"></span>\n')
        file_obj.write(f"{heading_text}\n\n")
    else:
        if anchor and options.use_toc_anchors:
            file_obj.write(f"\n## <a id=\"{anchor}\"></a>{heading_text}\n\n")
        else:
            file_obj.write(f"\n## {heading_text}\n\n")

def write_collapsible_open(file_obj, display_name: str, anchor: Optional[str], options: DocumentationOptions) -> None:
    """Open a <details> block in collapsible mode."""
    file_obj.write('\n<details open>\n')
    if options.use_minimal_format:
        if anchor and options.use_toc_anchors:
            file_obj.write(f'<summary><span id="{anchor}">{display_name}</span></summary>\n\n')
        else:
            file_obj.write(f'<summary><span>{display_name}</span></summary>\n\n')
    else:
        if anchor and options.use_toc_anchors:
            file_obj.write(f'<summary><h2 id="{anchor}" style="display:inline;">{display_name}</h2></summary>\n\n')
        else:
            file_obj.write(f'<summary><h2 style="display:inline;">{display_name}</h2></summary>\n\n')

def write_collapsible_close(file_obj) -> None:
    """Close a collapsible <details> block."""
    file_obj.write("</details>\n")


# ---------- Helper to Write a Section ----------

def write_section(
    file_obj,
    title: str,
    content_func: Callable[[], None],
    options: DocumentationOptions,
    initial_state: str = "open",
    is_subsection: bool = True
) -> None:
    """
    Write a block of text (title + content) in either normal or collapsible style.
    content_func() is called to write the body of the section.
    """
    anchor_id = make_anchor_id(title)
    should_collapse = (
        options.use_collapsible
        and options.collapsible_level != 'none'
        and (
            options.collapsible_level == 'all'
            or (options.collapsible_level == 'main' and not is_subsection)
            or (options.collapsible_level == 'subsections' and is_subsection)
        )
    )

    if should_collapse:
        file_obj.write(f'<details {initial_state}>\n')
        if options.use_minimal_format:
            file_obj.write(f'<summary><span id="{anchor_id}">{title}</span></summary>\n\n')
        else:
            file_obj.write(f'<summary><h2 id="{anchor_id}" style="display:inline;">{title}</h2></summary>\n\n')
        content_func()
        file_obj.write('\n</details>\n\n')
    else:
        if options.use_minimal_format:
            file_obj.write(f"{title}\n")
            content_func()
            file_obj.write("\n")
        else:
            file_obj.write(f"## {title}\n\n")
            content_func()
            file_obj.write("\n")


# ---------- Markdown Generation ----------

LANG_MAP = {
    '.swift': 'swift',
    '.metal': 'metal',
    '.py': 'python',
    '.md': 'markdown',
    '.json': 'json',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.sh': 'bash',
    '.cpp': 'cpp',
    '.h': 'cpp',
    '.c': 'c',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.html': 'html',
    '.css': 'css',
    '.txt': 'text',
    '.csv': 'csv',
    
    # Additional languages
    # Python related
    '.pyx': 'cython',
    '.pxd': 'cython',
    '.pyi': 'python',
    
    # Web development
    '.jsx': 'jsx',
    '.tsx': 'tsx',
    '.vue': 'vue',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.php': 'php',
    
    # Java ecosystem
    '.java': 'java',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.groovy': 'groovy',
    '.scala': 'scala',
    
    # .NET ecosystem
    '.cs': 'csharp',
    '.vb': 'vbnet',
    '.fs': 'fsharp',
    
    # Ruby ecosystem
    '.rb': 'ruby',
    '.erb': 'erb',
    '.rake': 'ruby',
    
    # Systems programming
    '.rs': 'rust',
    '.go': 'go',
    '.zig': 'zig',
    '.hpp': 'cpp',
    '.hxx': 'cpp',
    '.cxx': 'cpp',
    '.cc': 'cpp',
    
    # Shell scripting
    '.bash': 'bash',
    '.zsh': 'bash',
    '.fish': 'fish',
    '.ps1': 'powershell',
    
    # Config files
    '.toml': 'toml',
    '.ini': 'ini',
    '.xml': 'xml',
    '.conf': 'conf',
    
    # Database
    '.sql': 'sql',
    '.plsql': 'plsql',
    
    # Documentation
    '.rst': 'rst',
    '.tex': 'tex',
    '.adoc': 'asciidoc',
    
    # Mobile development
    '.m': 'objectivec',
    '.mm': 'objectivec',
    '.kt': 'kotlin',
    
    # Other
    '.r': 'r',
    '.lua': 'lua',
    '.pl': 'perl',
    '.pm': 'perl',
    '.elm': 'elm',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.erl': 'erlang',
    '.hrl': 'erlang',
    '.dart': 'dart',
    '.f90': 'fortran',
    '.f95': 'fortran',
    '.f03': 'fortran',
    '.ml': 'ocaml',
    '.mli': 'ocaml',
    '.hs': 'haskell',
    '.lhs': 'haskell',
    '.proto': 'protobuf',
    '.dockerfile': 'dockerfile',
    '.cmake': 'cmake',
    '.nim': 'nim',
    '.jl': 'julia'
}

def detect_language(ext: str) -> str:
    """Return the Markdown syntax highlighter language token for an extension."""
    return LANG_MAP.get(ext.lower(), "")

def create_markdown(
    project_dir: str,
    output_file: str,
    include_extensions: Set[str],
    show_extensions: Optional[Set[str]],
    options: DocumentationOptions
) -> None:
    """
    Generate the documentation in Markdown format.
    Collects files top-down, writes summary/tree/TOC if requested,
    then writes each file’s content.
    """
    project_dir_abs = os.path.abspath(project_dir)
    analyzer = ProjectAnalyzer(project_dir_abs)
    stats = analyzer.analyze_project()

    with open(output_file, 'w', encoding='utf-8') as f:
        proj_name = os.path.basename(project_dir_abs)

        # Top heading
        write_top_level_doc_heading(f, proj_name, options)

        # Summary
        if options.show_summary:
            def write_summary() -> None:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if options.use_minimal_format:
                    f.write(f"Generated on {now}\n\n")
                    f.write(f"- Directory: {project_dir_abs}\n")
                    f.write(f"- Total Files: {analyzer.file_count}\n")
                    f.write(f"- Total Lines: {analyzer.total_lines:,}\n\n")
                    if options.show_file_stats:
                        f.write("File Type Distribution\n\n")
                        for ext, count in sorted(stats.items()):
                            f.write(f"- {ext or '(no extension)'}: {count} files\n")
                        f.write("\n")
                else:
                    f.write(f"Generated on {now}\n\n")
                    f.write(f"- Directory: `{project_dir_abs}`\n")
                    f.write(f"- Total Files: {analyzer.file_count}\n")
                    f.write(f"- Total Lines: {analyzer.total_lines:,}\n\n")
                    if options.show_file_stats:
                        f.write("### File Type Distribution\n\n")
                        for ext, count in sorted(stats.items()):
                            f.write(f"- {ext or '(no extension)'}: {count} files\n")
                        f.write("\n")

            write_section(f, "Project Summary", write_summary, options, "open", False)

        # Tree
        if options.show_tree:
            def write_tree() -> None:
                tree_lines = generate_tree(
                    project_dir_abs,
                    show_extensions if (show_extensions and show_extensions != {'all'}) else None,
                    options.selected_folders
                )
                f.write("```\n")
                f.write("\n".join(tree_lines))
                f.write("\n```\n")

            write_section(f, "Project Tree", write_tree, options, "open", False)

        # Gather file list
        in_tree_files: List[str] = []
        collect_files_in_tree_order(
            project_dir_abs,
            in_tree_files,
            show_extensions if (show_extensions and show_extensions != {'all'}) else None,
            options.selected_folders,
            include_extensions
        )

        # TOC
        if options.show_toc:
            def write_toc() -> None:
                for full_path in in_tree_files:
                    rel_path = os.path.relpath(full_path, project_dir_abs)
                    display_name = format_path(rel_path, options.toc_format)
                    base_name = os.path.splitext(os.path.basename(rel_path))[0]
                    anchor = make_anchor_id(base_name)

                    if options.use_toc_anchors:
                        f.write(f"- [{display_name}](#{anchor})\n")
                    else:
                        f.write(f"- {display_name}\n")
                f.write("\n")

            write_section(f, "Table of Contents", write_toc, options, "open", False)

        # Write each file's content
        total_files = len(in_tree_files)
        start_time = time.time()

        for i, full_path in enumerate(in_tree_files, 1):
            # Progress bar (if enabled)
            if options.show_progress and total_files > 0:
                bar_line = draw_progress_bar(i, total_files, start_time, bar_len=30)
                sys.stdout.write(f"\r{bar_line}")
                sys.stdout.flush()

            file_info = analyzer.get_file_info(full_path)
            rel_path = os.path.relpath(full_path, project_dir_abs)
            display_name = format_path(rel_path, options.toc_format)
            base_name = os.path.splitext(os.path.basename(rel_path))[0]
            anchor = make_anchor_id(base_name)

            collapse_main = (
                options.use_collapsible
                and options.collapsible_level in ['all', 'main']
            )

            # Main heading
            if collapse_main:
                write_collapsible_open(f, display_name, anchor, options)
            else:
                write_main_heading(f, display_name, anchor, options)

            # File info section
            if options.show_file_info:
                def write_file_info() -> None:
                    if options.use_minimal_format:
                        if options.show_path_info:
                            f.write(f"Path: {rel_path}\n")
                        if options.show_sizes:
                            f.write(f"Size: {file_info.size} bytes\n")
                        if options.show_timestamps:
                            f.write(f"Last Modified: {format_time(file_info.last_modified)}\n")
                        if options.show_line_count and file_info.line_count is not None:
                            f.write(f"Lines: {file_info.line_count:,}\n")
                        f.write("\n")
                    else:
                        if options.show_path_info:
                            f.write(f"Path: `{rel_path}`\n\n")
                        if options.show_sizes:
                            f.write(f"Size: {format_size(file_info.size)}\n")
                        if options.show_timestamps:
                            f.write(f"Last Modified: {format_time(file_info.last_modified)}\n")
                        if options.show_line_count and file_info.line_count is not None:
                            f.write(f"Lines: {file_info.line_count:,}\n")
                        f.write("\n")

                write_section(f, "File Information", write_file_info, options)

            # Write code content
            ext = os.path.splitext(full_path)[1].lower()
            lang = detect_language(ext)
            chunks = chunked_file_reader(full_path, options.chunk_size)

            for idx, chunk in enumerate(chunks, 1):
                if len(chunks) > 1:
                    if options.use_minimal_format:
                        f.write(f"Part {idx}\n\n")
                    else:
                        f.write(f"### Part {idx}\n\n")

                if options.show_line_numbers:
                    start_line = (idx - 1) * options.chunk_size + 1
                    chunk = add_line_numbers(chunk, start_line)

                fence = f"```{lang}\n" if lang else "```\n"
                f.write(fence)
                f.write(chunk.rstrip())
                f.write("\n```\n\n")

            if collapse_main:
                write_collapsible_close(f)

        # End progress bar
        if options.show_progress and total_files > 0:
            sys.stdout.write("\n")
            sys.stdout.flush()

    _info_user(color_msg("\nDocumentation generated successfully!", "GREEN"))
    _info_user(f"Output file: {output_file}")
    _info_user(f"Files processed: {total_files}")

def format_path(path: str, format_type: str) -> str:
    """
    Convert a path to a user-chosen format:
      - 'full': full directory path
      - 'name_ext': just filename.ext
      - 'name': filename minus its extension
    """
    base = os.path.basename(path)
    if format_type == "full":
        return path
    elif format_type == "name_ext":
        return base
    return os.path.splitext(base)[0]


# ---------- Interactive Mode (Wizard) ----------

def interactive_mode() -> DocumentationOptions:
    """
    Step-by-step wizard to configure doc generation.
    Returns a filled DocumentationOptions object.
    """
    # Modern heading
    print(color_msg("==============================================", "CYAN"))
    print(color_msg("           DOCGEN INTERACTIVE WIZARD         ", "CYAN"))
    print(color_msg("==============================================", "CYAN"))
    print("\n")

    # Step 1: Optional Quick Report
    print(color_msg("Step 1: Optional Quick Report", "CYAN"))
    do_fast_report = get_yes_no_input("Generate a quick project report first?")
    if do_fast_report:
        while True:
            project_dir_temp = input("Directory for quick report (default='.'): ").strip() or '.'
            if os.path.isdir(project_dir_temp):
                print_fast_report(project_dir_temp)
                break
            _warn_user("Directory not found. Try again.")
        cont = get_yes_no_input("Continue to full wizard?")
        if not cont:
            print(color_msg("Exiting after quick report.", "YELLOW"))
            sys.exit(0)
    print("\n")

    # Step 2: Select Project Directory
    print(color_msg("Step 2: Select Project Directory", "CYAN"))
    while True:
        project_dir = input("Project directory (default='.'): ").strip() or '.'
        if os.path.isdir(project_dir):
            break
        _warn_user("Directory not found. Try again.")
    print("\n")

    # Quick analysis
    print(color_msg("Analyzing project structure...", "CYAN"))
    analyzer = ProjectAnalyzer(project_dir)
    stats = analyzer.analyze_project()
    print(f"Found in {project_dir}:")  # Normal color
    for ext, count in sorted(stats.items()):
        print(f"  {ext}: {count} files")
    print("\n")

    # Step 3: Choose File Types
    print(color_msg("Step 3: Choose File Types to Include", "CYAN"))
    print("Enter comma-separated extensions (e.g. 'py,md') or '*' for all.")
    include = input("Extensions > ").strip() or '*'
    print("\n")

    # Step 4: Limit to Specific Subfolders
    print(color_msg("Step 4: Limit to Specific Subfolders", "CYAN"))
    limit_folders = get_yes_no_input("Restrict to certain subfolders?", False)
    if limit_folders:
        print("Enter comma-separated subfolder names or paths.")
        folder_string = input("Folders > ").strip() or ''
        selected_folders = parse_folders(folder_string, project_dir)
    else:
        selected_folders = None
    print("\n")

    # Step 5: Display Options
    print(color_msg("Step 5: Display Options", "CYAN"))
    show_tree = get_yes_no_input("Show a project tree?")
    show_toc = get_yes_no_input("Show a table of contents?", True)

    toc_format = 'name_ext'
    use_toc_anchors = False
    toc_anchor_style = 'simple'

    if show_toc:
        print("\n")
        print("How should files be labeled in the TOC?")
        print("  1. Full paths (dir/subdir/file.ext)")
        print("  2. Filename with extension (file.ext)")
        print("  3. Just filename (file)")
        toc_choice = input("Choice > ").strip()
        toc_format = {'1': 'full', '2': 'name_ext', '3': 'name'}.get(toc_choice, 'name_ext')

        use_toc_anchors = get_yes_no_input("Include clickable links in TOC?", True)
        if use_toc_anchors:
            print("\n")
            print("How should TOC anchors be formed?")
            print("  1. Simple (filename only)")
            print("  2. Full path-based anchors")
            anchor_choice = input("Choice > ").strip()
            toc_anchor_style = 'simple' if anchor_choice == '1' else 'full_path'
    print("\n")

    # Step 6: Summaries & Collapsible
    print(color_msg("Step 6: Summaries & Collapsible Settings", "CYAN"))
    show_summary = get_yes_no_input("Show a project summary?", True)
    use_collapsible = get_yes_no_input("Use collapsible sections?", True)
    if use_collapsible:
        print("\n")
        print("Which sections should collapse?")
        print("  1. All (main & subsections)")
        print("  2. Only main sections")
        print("  3. Only subsections")
        c_choice = input("Choice > ").strip()
        collapsible_level = {'1': 'all', '2': 'main', '3': 'subsections'}.get(c_choice, 'all')
    else:
        collapsible_level = 'none'
    use_minimal_format = get_yes_no_input("Use minimal formatting?", False)
    print("\n")

    # Step 7: Tree Detail (if enabled)
    print(color_msg("Step 7: Tree Detail (if tree is enabled)", "CYAN"))
    show_all = False
    show_exts = None
    if show_tree:
        print("How should the tree be filtered?")
        print("  1. Same as included file types")
        print("  2. Show all files")
        print("  3. Custom extension list")
        tree_choice = input("Choice > ").strip()

        if tree_choice == '2':
            show_all = True
        elif tree_choice == '1':
            show_exts = include
        elif tree_choice == '3':
            show_exts = input("Extensions for tree (e.g. 'md,py') > ").strip()
    print("\n")

    # Step 8: Detailed File Information
    print(color_msg("Step 8: Detailed File Information", "CYAN"))
    show_file_info = get_yes_no_input("Show file info sections?")
    if show_file_info:
        show_line_count = get_yes_no_input("Include line counts?")
        show_file_stats = get_yes_no_input("Include file type stats?")
        show_timestamps = get_yes_no_input("Show last modified timestamps?")
        show_sizes = get_yes_no_input("Show file sizes?")
        show_path_info = get_yes_no_input("Show full path in info?", False)
    else:
        show_line_count = False
        show_file_stats = False
        show_timestamps = False
        show_sizes = False
        show_path_info = False

    show_line_numbers = get_yes_no_input("Show line numbers in code blocks?", False)
    print("\n")

    # Step 9: Advanced Options
    print(color_msg("Step 9: Advanced Options", "CYAN"))
    user_chunk = input("Lines per code block [default=200] > ").strip()
    chunk_size = int(user_chunk) if user_chunk.isdigit() else 200
    show_progress = get_yes_no_input("Show a progress bar during generation?", True)
    print("\n")

    # Output Setup
    print(color_msg("Final: Output Setup", "CYAN"))
    output_file = input("Output file (default='project_code_documentation.md') > ").strip() or "project_code_documentation.md"
    print("\n")

    # CLI Command (Optional)
    print(color_msg("Optional: Generate a CLI Command", "CYAN"))
    want_cli = get_yes_no_input("Show a CLI command replicating these settings?", default=False)
    print("\n")  # Add space before Review

    # Review & Confirm
    print(color_msg("Review & Confirm", "CYAN"))
    print(color_msg("----------------------------------------------", "CYAN"))
    print(color_msg("Directory:", "CYAN") + f" {project_dir}")
    print(color_msg("Extensions:", "CYAN") + f" {include}")
    print(color_msg("Selected Folders:", "CYAN") + f" {selected_folders}")
    print(color_msg("Collapsible:", "CYAN") + f" {use_collapsible}" + color_msg(" (Level:", "CYAN") + f" {collapsible_level}" + color_msg(")", "CYAN"))
    print(color_msg("Minimal Format:", "CYAN") + f" {use_minimal_format}")
    print(color_msg("Line Numbers:", "CYAN") + f" {show_line_numbers}")
    print(color_msg("Chunk Size:", "CYAN") + f" {chunk_size}")
    print(color_msg("Show Progress:", "CYAN") + f" {show_progress}")
    print(color_msg("Output File:", "CYAN") + f" {output_file}")
    print()

    if want_cli:
        print(color_msg("Equivalent CLI Command:", "CYAN"))
        
        # Build the command string
        cmd = ["python3 docgen.py"]
        
        # Add basic options
        if project_dir != ".":
            cmd.append(f'"{project_dir}"')
        if output_file != "project_code_documentation.md":
            cmd.append(f'-o "{output_file}"')
            
        # Add feature flags
        if include != "*":
            cmd.append(f'--include "{include}"')
        if selected_folders:
            folders_str = ",".join(os.path.relpath(f, project_dir) for f in selected_folders)
            cmd.append(f'--folders "{folders_str}"')
        if show_tree:
            if show_all:
                cmd.append("--show-all")
            elif show_exts and show_exts != include:
                cmd.append(f'--show "{show_exts}"')
        
        # Add boolean flags
        if not show_summary:
            cmd.append("--no-summary")
        if not show_tree:
            cmd.append("--no-tree")
        if not show_file_info:
            cmd.append("--no-file-info")
        if not show_line_count:
            cmd.append("--no-line-count")
        if not show_file_stats:
            cmd.append("--no-file-stats")
        if not show_timestamps:
            cmd.append("--no-timestamps")
        if not show_sizes:
            cmd.append("--no-sizes")
        if not show_toc:
            cmd.append("--no-toc")
        if not use_toc_anchors:
            cmd.append("--no-toc-anchors")
        
        # Add value-based options
        if use_minimal_format:
            cmd.append("--minimal")
        if show_line_numbers:
            cmd.append("--line-numbers")
        if show_path_info:
            cmd.append("--path-info")
        if chunk_size != 200:
            cmd.append(f"--chunk-size {chunk_size}")
        if show_progress:
            cmd.append("--show-progress")
        if toc_format != "name_ext":
            cmd.append(f"--toc-format {toc_format}")
        if toc_anchor_style != "simple":
            cmd.append(f"--toc-anchor-style {toc_anchor_style}")
        if use_collapsible and collapsible_level != "all":
            cmd.append(f"--collapsible-level {collapsible_level}")
        elif not use_collapsible:
            cmd.append("--no-collapsible")
            
        # Print the complete command
        print(" ".join(cmd))
        print()

    proceed = get_yes_no_input("Proceed with these settings?", True)
    print("\n")  # Add space before progress bar
    if not proceed:
        print(color_msg("Aborted by user.", "YELLOW"))
        sys.exit(0)

    return DocumentationOptions(
        project_dir=project_dir,
        output_file=output_file,
        include_extensions=include,
        show_extensions=show_exts if show_exts else include,
        show_all=show_all,
        show_file_info=show_file_info,
        show_tree=show_tree,
        show_line_count=show_line_count,
        show_file_stats=show_file_stats,
        show_timestamps=show_timestamps,
        show_sizes=show_sizes,
        show_summary=show_summary,
        use_collapsible=use_collapsible,
        collapsible_level=collapsible_level,
        use_minimal_format=use_minimal_format,
        show_line_numbers=show_line_numbers,
        show_toc=show_toc,
        toc_format=toc_format,
        use_toc_anchors=use_toc_anchors,
        toc_anchor_style=toc_anchor_style,
        show_path_info=show_path_info,
        chunk_size=chunk_size,
        show_progress=show_progress,
        selected_folders=selected_folders
    )


# ---------- Main Entry Point ----------

def main() -> None:
    """
    Parse CLI arguments or start interactive mode. Generate Markdown docs from a project directory.
    """
    # A more modern usage and description with cyan color
    description = (
        color_msg("==============================================\n", "CYAN") +
        color_msg("                 DOCGEN INFO                 \n", "CYAN") +
        color_msg("==============================================\n", "CYAN") +
        "\nGenerate structured Markdown documentation for a project.\n"
    )
    epilog = f"""
Examples:
  {color_msg("python3 docgen.py .", "CYAN")}                Comprehensive documentation of current directory
  {color_msg("python3 docgen.py -i", "CYAN")}               Launch interactive wizard
  {color_msg("python3 docgen.py --fast-report", "CYAN")}    Quick project report and exit
  {color_msg("python3 docgen.py --include py", "CYAN")}     Include only .py files
  {color_msg("python3 docgen.py . -o docs.md --include 'py,md' --folders 'src,tests' --show-progress", "CYAN")}
"""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
        usage=color_msg("docgen.py [options] [project_dir]", "CYAN")
    )

    main_group = parser.add_argument_group(color_msg("Main Options", "CYAN"))
    main_group.add_argument("--version", action="version",
                            version=color_msg("py-code-docgen", "CYAN") +
                            f" v{color_msg(__version__, 'GREEN')}")
    main_group.add_argument("-i", "--interactive", action="store_true",
                            help="Launch the interactive wizard")
    main_group.add_argument("--fast-report", action="store_true",
                            help="Generate a quick project report and exit")
    main_group.add_argument("project_dir", nargs="?", default=".",
                            help="Project directory (default: current)")
    main_group.add_argument("-o", "--output", default="project_code_documentation.md",
                            help="Output file name (default: project_code_documentation.md)")

    content_group = parser.add_argument_group(color_msg("Content Options", "CYAN"))
    content_group.add_argument("--include", default="*",
                               help="Comma-separated extensions, or 'all/*' for everything")
    content_group.add_argument("--show", default=None,
                               help="Extensions to show in tree view (optional)")
    content_group.add_argument("--show-all", action="store_true",
                               help="Show all files in tree, ignoring extension filters")
    content_group.add_argument("--folders", default=None,
                               help="Comma-separated subfolders within project_dir")

    format_group = parser.add_argument_group(color_msg("Format Options", "CYAN"))
    format_group.add_argument("--no-collapsible", action="store_true",
                              help="Disable collapsible sections")
    format_group.add_argument("--collapsible-level", choices=["all", "main", "subsections", "none"],
                              default="all", help="Level of collapsible sections if enabled")
    format_group.add_argument("--minimal", action="store_true",
                              help="Use minimal formatting in the final Markdown")
    format_group.add_argument("--line-numbers", action="store_true",
                              help="Show line numbers in code blocks")

    display_group = parser.add_argument_group(color_msg("Display Options", "CYAN"))
    display_group.add_argument("--no-summary", action="store_true",
                               help="Hide the summary section")
    display_group.add_argument("--no-tree", action="store_true",
                               help="Hide the project tree")
    display_group.add_argument("--no-file-info", action="store_true",
                               help="Hide the file info sections")
    display_group.add_argument("--no-line-count", action="store_true",
                               help="Hide line counts")
    display_group.add_argument("--no-file-stats", action="store_true",
                               help="Hide extension distribution stats")
    display_group.add_argument("--no-timestamps", action="store_true",
                               help="Hide timestamps in file info")
    display_group.add_argument("--no-sizes", action="store_true",
                               help="Hide file sizes in file info")

    toc_group = parser.add_argument_group(color_msg("TOC Options", "CYAN"))
    toc_group.add_argument("--no-toc", action="store_true",
                           help="Hide the table of contents")
    toc_group.add_argument("--toc-format", choices=["full", "name_ext", "name"], default="name_ext",
                           help="How file names are shown in the TOC")
    toc_group.add_argument("--no-toc-anchors", action="store_true",
                           help="Disable clickable TOC anchors")
    toc_group.add_argument("--toc-anchor-style", choices=["simple", "full_path"], default="simple",
                           help="Anchor style in the TOC")

    adv_group = parser.add_argument_group(color_msg("Advanced Options", "CYAN"))
    adv_group.add_argument("--path-info", action="store_true",
                           help="Show file path info in the File Info sections")
    adv_group.add_argument("--chunk-size", type=int, default=200,
                           help="Lines per code block chunk (default=200)")
    adv_group.add_argument("--show-progress", action="store_true",
                           help="Show a progress bar during doc generation")

    args = parser.parse_args()

    try:
        if args.fast_report:
            print_fast_report(args.project_dir)
            sys.exit(0)

        if args.interactive:
            # Wizard
            options = interactive_mode()
            include_exts = parse_extensions(options.include_extensions)
            show_exts = None if options.show_all else (
                parse_extensions(options.show_extensions) if options.show_extensions else include_exts
            )
        else:
            # Direct CLI
            use_collapse = not args.no_collapsible
            collapsible_level = args.collapsible_level if use_collapse else "none"
            selected_folders = parse_folders(args.folders, args.project_dir)

            options = DocumentationOptions(
                project_dir=args.project_dir,
                output_file=args.output,
                include_extensions=args.include,
                show_extensions=args.show or args.include,
                show_all=args.show_all,
                show_file_info=not args.no_file_info,
                show_tree=not args.no_tree,
                show_line_count=not args.no_line_count,
                show_file_stats=not args.no_file_stats,
                show_timestamps=not args.no_timestamps,
                show_sizes=not args.no_sizes,
                show_summary=not args.no_summary,
                use_collapsible=use_collapse,
                collapsible_level=collapsible_level,
                use_minimal_format=args.minimal,
                show_line_numbers=args.line_numbers,
                show_toc=not args.no_toc,
                toc_format=args.toc_format,
                use_toc_anchors=not args.no_toc_anchors,
                toc_anchor_style=args.toc_anchor_style,
                show_path_info=args.path_info,
                chunk_size=args.chunk_size,
                show_progress=args.show_progress,
                selected_folders=selected_folders
            )

            include_exts = parse_extensions(options.include_extensions)
            show_exts = None if options.show_all else (
                parse_extensions(options.show_extensions) if options.show_extensions else include_exts
            )

        create_markdown(
            options.project_dir,
            options.output_file,
            include_exts,
            show_exts,
            options
        )
    except Exception as ex:
        _error_user(str(ex))
        sys.exit(1)

if __name__ == "__main__":
    main()
