#!/usr/bin/env python3
"""
TreeTool - Professional Directory Structure Visualizer
=======================================================

A CLI tool to generate beautiful ASCII/Unicode tree representations
of directory structures for documentation purposes.

Author: handsomejack
License: Apache-2.0
"""

import argparse
import os
import sys
import fnmatch
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Set, TextIO
from enum import Enum


# =============================================================================
# Constants & Configuration
# =============================================================================

VERSION = "1.0.0"

class TreeStyle(Enum):
    """Available tree drawing styles."""
    ASCII = "ascii"
    UNICODE = "unicode"
    BOLD = "bold"
    MINIMAL = "minimal"


# Style definitions: (branch, last_branch, vertical, space)
STYLES = {
    TreeStyle.ASCII: ("|-- ", "+-- ", "|   ", "    "),
    TreeStyle.UNICODE: ("├── ", "└── ", "│   ", "    "),
    TreeStyle.BOLD: ("┣━━ ", "┗━━ ", "┃   ", "    "),
    TreeStyle.MINIMAL: ("|-- ", "`-- ", "|   ", "    "),
}

# Preset ignore patterns
PRESETS = {
    "python": [
        "__pycache__", "*.pyc", "*.pyo", "*.pyd", ".Python",
        "*.so", ".venv", "venv", "ENV", "env",
        "*.egg-info", "*.egg", "dist", "build",
        ".pytest_cache", ".mypy_cache", ".tox",
        "*.py[cod]", ".coverage", "htmlcov",
    ],
    "node": [
        "node_modules", "npm-debug.log*", "yarn-debug.log*",
        "yarn-error.log*", ".npm", ".yarn", "dist",
        "build", ".next", ".nuxt", "coverage",
    ],
    "git": [
        ".git", ".gitignore", ".gitattributes", ".gitmodules",
    ],
    "ide": [
        ".idea", ".vscode", "*.swp", "*.swo", "*~",
        ".project", ".settings", ".classpath",
        "*.sublime-*", ".atom",
    ],
    "all": [],  # Will be populated with all presets combined
}

# Combine all presets into 'all'
PRESETS["all"] = list(set(
    pattern for preset in ["python", "node", "git", "ide"] 
    for pattern in PRESETS[preset]
))


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TreeConfig:
    """Configuration for tree generation."""
    root_path: Path
    max_depth: Optional[int] = None
    dirs_only: bool = False
    files_only: bool = False
    alphabetic: bool = False
    style: TreeStyle = TreeStyle.ASCII
    show_stats: bool = False
    use_color: bool = False
    ignore_patterns: Set[str] = field(default_factory=set)
    ignore_hidden: bool = False


@dataclass
class TreeStats:
    """Statistics about the generated tree."""
    total_dirs: int = 0
    total_files: int = 0
    max_depth_reached: int = 0


# =============================================================================
# Color Output
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[32m"
    BRIGHT_GREEN = "\033[92m"
    RESET = "\033[0m"
    BG_BLACK = "\033[40m"
    
    @classmethod
    def colorize(cls, text: str, enabled: bool = True) -> str:
        """Apply green-on-black coloring if enabled."""
        if not enabled:
            return text
        return f"{cls.BG_BLACK}{cls.BRIGHT_GREEN}{text}{cls.RESET}"


# =============================================================================
# Ignore Pattern Handling
# =============================================================================

class IgnorePatternMatcher:
    """Handles ignore pattern matching similar to .gitignore."""
    
    def __init__(self, patterns: Set[str]):
        self.patterns = patterns
    
    def should_ignore(self, name: str, is_dir: bool = False) -> bool:
        """Check if a file/directory should be ignored."""
        for pattern in self.patterns:
            # Handle directory-specific patterns (ending with /)
            if pattern.endswith('/'):
                if is_dir and fnmatch.fnmatch(name, pattern[:-1]):
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(name, pattern):
                return True
            # Exact match
            elif name == pattern:
                return True
        return False
    
    @classmethod
    def from_file(cls, filepath: Path) -> 'IgnorePatternMatcher':
        """Load patterns from an ignore file."""
        patterns = set()
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.add(line)
        return cls(patterns)


# =============================================================================
# Tree Generator
# =============================================================================

class TreeGenerator:
    """Generates ASCII/Unicode tree representation of directory structures."""
    
    def __init__(self, config: TreeConfig):
        self.config = config
        self.stats = TreeStats()
        self.style_chars = STYLES[config.style]
        self.matcher = IgnorePatternMatcher(config.ignore_patterns)
        self.output_lines: List[str] = []
    
    def generate(self) -> str:
        """Generate the complete tree representation."""
        self.output_lines = []
        self.stats = TreeStats()
        
        root_name = self.config.root_path.name or str(self.config.root_path)
        self.output_lines.append(root_name)
        
        self._walk_directory(self.config.root_path, "", 0)
        
        if self.config.show_stats:
            self._append_stats()
        
        return "\n".join(self.output_lines)
    
    def _walk_directory(self, path: Path, prefix: str, depth: int) -> None:
        """Recursively walk directory and build tree representation."""
        # Check depth limit
        if self.config.max_depth is not None and depth >= self.config.max_depth:
            return
        
        # Update max depth stat
        if depth > self.stats.max_depth_reached:
            self.stats.max_depth_reached = depth
        
        # Get and filter entries
        try:
            entries = list(path.iterdir())
        except PermissionError:
            return
        
        # Filter entries
        filtered_entries = []
        for entry in entries:
            # Skip hidden files if configured
            if self.config.ignore_hidden and entry.name.startswith('.'):
                continue
            
            # Check ignore patterns
            if self.matcher.should_ignore(entry.name, entry.is_dir()):
                continue
            
            # Filter by type
            if self.config.dirs_only and not entry.is_dir():
                continue
            if self.config.files_only and entry.is_dir():
                continue
            
            filtered_entries.append(entry)
        
        # Sort entries
        if self.config.alphabetic:
            filtered_entries.sort(key=lambda e: e.name.lower())
        else:
            # Default: directories first, then files
            dirs = sorted([e for e in filtered_entries if e.is_dir()], 
                         key=lambda e: e.name.lower())
            files = sorted([e for e in filtered_entries if e.is_file()], 
                          key=lambda e: e.name.lower())
            filtered_entries = dirs + files
        
        # Generate tree lines
        branch, last_branch, vertical, space = self.style_chars
        
        for i, entry in enumerate(filtered_entries):
            is_last = (i == len(filtered_entries) - 1)
            connector = last_branch if is_last else branch
            
            # Add entry to output
            line = f"{prefix}{connector}{entry.name}"
            if entry.is_dir():
                line += "/"
                self.stats.total_dirs += 1
            else:
                self.stats.total_files += 1
            
            self.output_lines.append(line)
            
            # Recurse into directories
            if entry.is_dir():
                new_prefix = prefix + (space if is_last else vertical)
                self._walk_directory(entry, new_prefix, depth + 1)
    
    def _append_stats(self) -> None:
        """Append statistics to output."""
        self.output_lines.append("")
        self.output_lines.append("-" * 40)
        self.output_lines.append(f"Directories: {self.stats.total_dirs}")
        self.output_lines.append(f"Files:       {self.stats.total_files}")
        self.output_lines.append(f"Max Depth:   {self.stats.max_depth_reached}")
        self.output_lines.append("-" * 40)


# =============================================================================
# Output Formatters
# =============================================================================

class OutputFormatter:
    """Handles output formatting for different file types."""
    
    @staticmethod
    def format_markdown(tree: str, root_path: str) -> str:
        """Format tree output for Markdown files."""
        lines = [
            f"# Directory Structure: `{root_path}`",
            "",
            "```",
            tree,
            "```",
            "",
            f"*Generated with TreeTool v{VERSION}*",
        ]
        return "\n".join(lines)
    
    @staticmethod
    def format_text(tree: str, root_path: str) -> str:
        """Format tree output for plain text files."""
        lines = [
            f"Directory Structure: {root_path}",
            "=" * 50,
            "",
            tree,
            "",
            "=" * 50,
            f"Generated with TreeTool v{VERSION}",
        ]
        return "\n".join(lines)


# =============================================================================
# CLI Argument Parser
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="treetool",
        description="Generate beautiful ASCII tree representations of directory structures.",
        epilog="Examples:\n"
               "  %(prog)s .                          # Current directory\n"
               "  %(prog)s ./src --depth 3            # Limit depth to 3\n"
               "  %(prog)s . --preset python -o tree.md  # Python project as MD\n"
               "  %(prog)s . --style unicode --color  # Unicode style with colors\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root directory path (default: current directory)"
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Output file (.txt or .md). If not specified, prints to stdout."
    )
    output_group.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics (directory/file counts)"
    )
    output_group.add_argument(
        "--color",
        action="store_true",
        help="Enable colored output (green on black)"
    )
    
    # Filter options
    filter_group = parser.add_argument_group("Filter Options")
    filter_group.add_argument(
        "-d", "--depth",
        type=int,
        metavar="N",
        help="Maximum depth to display (default: unlimited)"
    )
    filter_group.add_argument(
        "--dirs-only",
        action="store_true",
        help="Show only directories"
    )
    filter_group.add_argument(
        "--files-only",
        action="store_true",
        help="Show only files"
    )
    filter_group.add_argument(
        "--no-hidden",
        action="store_true",
        help="Exclude hidden files and directories"
    )
    
    # Ignore patterns
    ignore_group = parser.add_argument_group("Ignore Patterns")
    ignore_group.add_argument(
        "-p", "--preset",
        choices=["python", "node", "git", "ide", "all"],
        action="append",
        default=[],
        help="Use preset ignore patterns (can be used multiple times)"
    )
    ignore_group.add_argument(
        "-i", "--ignore-file",
        metavar="FILE",
        help="Path to ignore file (similar to .gitignore format)"
    )
    ignore_group.add_argument(
        "-e", "--exclude",
        metavar="PATTERN",
        action="append",
        default=[],
        help="Exclude pattern (can be used multiple times)"
    )
    
    # Style options
    style_group = parser.add_argument_group("Style Options")
    style_group.add_argument(
        "-s", "--style",
        choices=["ascii", "unicode", "bold", "minimal"],
        default="ascii",
        help="Tree drawing style (default: ascii)"
    )
    style_group.add_argument(
        "-a", "--alphabetic",
        action="store_true",
        help="Sort alphabetically (default: directories first)"
    )
    
    return parser


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate path
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}", file=sys.stderr)
        return 1
    if not root_path.is_dir():
        print(f"Error: Path is not a directory: {root_path}", file=sys.stderr)
        return 1
    
    # Collect ignore patterns
    ignore_patterns: Set[str] = set()
    
    # Add preset patterns
    for preset in args.preset:
        ignore_patterns.update(PRESETS[preset])
    
    # Add patterns from ignore file
    if args.ignore_file:
        ignore_file = Path(args.ignore_file)
        if not ignore_file.exists():
            print(f"Error: Ignore file not found: {ignore_file}", file=sys.stderr)
            return 1
        matcher = IgnorePatternMatcher.from_file(ignore_file)
        ignore_patterns.update(matcher.patterns)
    
    # Add explicit exclude patterns
    ignore_patterns.update(args.exclude)
    
    # Validate mutually exclusive options
    if args.dirs_only and args.files_only:
        print("Error: --dirs-only and --files-only are mutually exclusive", 
              file=sys.stderr)
        return 1
    
    # Create configuration
    config = TreeConfig(
        root_path=root_path,
        max_depth=args.depth,
        dirs_only=args.dirs_only,
        files_only=args.files_only,
        alphabetic=args.alphabetic,
        style=TreeStyle(args.style),
        show_stats=args.stats,
        use_color=args.color and not args.output,  # No color for file output
        ignore_patterns=ignore_patterns,
        ignore_hidden=args.no_hidden,
    )
    
    # Generate tree
    generator = TreeGenerator(config)
    tree_output = generator.generate()
    
    # Handle output
    if args.output:
        output_path = Path(args.output)
        
        # Determine format by extension
        if output_path.suffix.lower() == ".md":
            content = OutputFormatter.format_markdown(tree_output, root_path.name)
        else:
            content = OutputFormatter.format_text(tree_output, root_path.name)
        
        # Write file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Tree saved to: {output_path}")
        except IOError as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return 1
    else:
        # Print to stdout
        if config.use_color:
            print(Colors.colorize(tree_output))
        else:
            print(tree_output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

