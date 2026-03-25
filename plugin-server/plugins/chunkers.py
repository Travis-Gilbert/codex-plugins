"""
Source code chunkers for the ingestion pipeline.

Phase 1: AST-based Python chunking, regex-based JS/TS chunking,
header-based Markdown splitting. Files under 200 lines stored as
single "module" chunks.
"""

import ast
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_type: str  # function, class, module, section, config
    symbol_name: str
    content: str
    start_line: int
    end_line: int


# ---------- Python chunker (AST-based) ----------

def chunk_python(source: str, max_single_file_lines: int = 200) -> list[Chunk]:
    """Split Python source into function/class chunks using the AST."""
    lines = source.splitlines()
    if len(lines) <= max_single_file_lines:
        return [Chunk("module", "", source, 0, len(lines))]

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [Chunk("module", "", source, 0, len(lines))]

    chunks = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno - 1
            end = node.end_lineno or node.lineno
            chunks.append(Chunk(
                "function",
                node.name,
                "\n".join(lines[start:end]),
                start,
                end,
            ))
        elif isinstance(node, ast.ClassDef):
            start = node.lineno - 1
            end = node.end_lineno or node.lineno
            chunks.append(Chunk(
                "class",
                node.name,
                "\n".join(lines[start:end]),
                start,
                end,
            ))

    if not chunks:
        return [Chunk("module", "", source, 0, len(lines))]

    return chunks


# ---------- JavaScript / TypeScript chunker (regex) ----------

_JS_PATTERNS = [
    # Named function declarations
    re.compile(
        r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)",
        re.MULTILINE,
    ),
    # Arrow / const function
    re.compile(
        r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>",
        re.MULTILINE,
    ),
    # Class declarations
    re.compile(
        r"^(?:export\s+)?class\s+(\w+)",
        re.MULTILINE,
    ),
]


def chunk_javascript(source: str, max_single_file_lines: int = 200) -> list[Chunk]:
    """Split JS/TS source into chunks using regex heuristics."""
    lines = source.splitlines()
    if len(lines) <= max_single_file_lines:
        return [Chunk("module", "", source, 0, len(lines))]

    # Find all top-level definitions
    boundaries = []
    for pattern in _JS_PATTERNS:
        for match in pattern.finditer(source):
            line_no = source[:match.start()].count("\n")
            name = match.group(1)
            is_class = "class" in match.group(0).split(name)[0]
            boundaries.append((line_no, name, "class" if is_class else "function"))

    if not boundaries:
        return [Chunk("module", "", source, 0, len(lines))]

    boundaries.sort(key=lambda b: b[0])

    chunks = []
    for i, (start, name, ctype) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(lines)
        content = "\n".join(lines[start:end]).rstrip()
        if content:
            chunks.append(Chunk(ctype, name, content, start, end))

    return chunks


# ---------- Markdown chunker (header-based) ----------

_MD_HEADER = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def chunk_markdown(source: str) -> list[Chunk]:
    """Split Markdown into sections by headers."""
    lines = source.splitlines()
    if not lines:
        return []

    headers = list(_MD_HEADER.finditer(source))
    if not headers:
        return [Chunk("section", "", source, 0, len(lines))]

    chunks = []
    for i, match in enumerate(headers):
        start = source[:match.start()].count("\n")
        if i + 1 < len(headers):
            end = source[:headers[i + 1].start()].count("\n")
        else:
            end = len(lines)
        name = match.group(2).strip()
        content = "\n".join(lines[start:end]).rstrip()
        if content:
            chunks.append(Chunk("section", name, content, start, end))

    return chunks


# ---------- Dispatcher ----------

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".md": "markdown",
    ".json": "json",
}


def detect_language(file_path: str) -> str:
    """Detect language from file extension."""
    for ext, lang in LANGUAGE_MAP.items():
        if file_path.endswith(ext):
            return lang
    return "other"


def chunk_source(source: str, file_path: str) -> list[Chunk]:
    """Dispatch to the appropriate chunker based on file type."""
    lang = detect_language(file_path)
    if lang == "python":
        return chunk_python(source)
    elif lang in ("javascript", "typescript"):
        return chunk_javascript(source)
    elif lang == "markdown":
        return chunk_markdown(source)
    else:
        # Store whole file as single chunk
        lines = source.splitlines()
        return [Chunk("module", "", source, 0, len(lines))]
