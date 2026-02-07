#!/usr/bin/env python3
"""Extract summary docstring from Python files.

Usage: extract-summary.py <filepath>
Output: First line of the main class or module docstring (stdout).
"""

import ast
import sys


def extract_summary(filepath: str) -> str:
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())
    except (SyntaxError, FileNotFoundError, PermissionError):
        return ""

    # Try first class docstring
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            if docstring:
                return docstring.split("\n")[0].strip()

    # Fallback to module docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        return module_doc.split("\n")[0].strip()

    return ""


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    result = extract_summary(sys.argv[1])
    if result:
        print(result)
