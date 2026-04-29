#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "public" / "abracapocus_articles"
OUTPUT_DIR = ROOT / "src" / "content" / "articles"


def fail(message: str) -> None:
    print(f"convert_articles.py: {message}", file=sys.stderr)
    sys.exit(1)


def yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def title_from_filename(path: Path) -> str:
    return re.sub(r"^\d+\.\s*", "", path.stem).strip()


def order_from_filename(path: Path) -> int:
    match = re.match(r"^(\d+)\.\s+", path.name)
    if not match:
        fail(f"article filename must start with an order number: {path.name}")
    return int(match.group(1))


def slugify(value: str) -> str:
    slug = value.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def is_heading(line: str) -> bool:
    return bool(re.match(r"^\s{0,3}#{1,6}\s+\S", line))


def is_bold_heading(line: str) -> bool:
    return bool(re.match(r"^\*\*[^*].*[^*]\*\*$", line.strip()))


def strip_leading_title(markdown: str) -> str:
    lines = markdown.strip().splitlines()
    index = 0

    while index < len(lines):
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index < len(lines) and (is_heading(lines[index]) or is_bold_heading(lines[index])):
            index += 1
            continue
        break

    return "\n".join(lines[index:]).strip() + "\n"


def normalize_bold_headings(markdown: str) -> str:
    lines = []
    for line in markdown.splitlines():
        stripped = line.strip()
        match = re.match(r"^\*\*(.+)\*\*$", stripped)
        if match:
            lines.append(f"## {match.group(1).strip()}")
        else:
            lines.append(line)
    return "\n".join(lines).strip() + "\n"


def description_from_body(markdown: str) -> str:
    for paragraph in re.split(r"\n\s*\n", markdown):
        text = paragraph.strip()
        if not text or text.startswith("#"):
            continue
        text = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"[*_`>#]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 180:
            text = text[:177].rsplit(" ", 1)[0].rstrip() + "..."
        return text
    return ""


def convert_docx(path: Path) -> str:
    result = subprocess.run(
        ["pandoc", "--from=docx", "--to=gfm", "--wrap=none", str(path)],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    body = strip_leading_title(result.stdout)
    return normalize_bold_headings(body)


def main() -> None:
    if shutil.which("pandoc") is None:
        fail("Pandoc is required to convert article docx files. Install pandoc and rerun this script.")

    docx_files = sorted(SOURCE_DIR.glob("*.docx"), key=order_from_filename)
    if not docx_files:
        fail(f"expected .docx files in {SOURCE_DIR}, found none")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for docx in docx_files:
        title = title_from_filename(docx)
        slug = slugify(title)
        order = order_from_filename(docx)
        source_docx = docx.relative_to(ROOT / "public").as_posix()
        body = convert_docx(docx)
        description = description_from_body(body)

        frontmatter = "\n".join(
            [
                "---",
                f"title: {yaml_string(title)}",
                f"slug: {yaml_string(slug)}",
                f"order: {order}",
                f"source_docx: {yaml_string(source_docx)}",
                f"description: {yaml_string(description)}",
                "---",
                "",
            ]
        )
        (OUTPUT_DIR / f"{slug}.md").write_text(frontmatter + body, encoding="utf-8")
        print(f"wrote src/content/articles/{slug}.md")


if __name__ == "__main__":
    main()
