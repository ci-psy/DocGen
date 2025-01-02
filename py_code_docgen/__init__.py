#!/usr/bin/env python3
import os
import datetime
import sys
import argparse
from pathlib import Path
from typing import Set, List, Dict, Optional, NamedTuple, Callable
from dataclasses import dataclass
import tqdm

__version__ = "0.1.8"

# ANSI escape codes for color and styling
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

[... rest of the file remains exactly the same ...]
