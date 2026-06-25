import argparse
import html
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


DDL_PATTERNS = [
    ("PROCEDURE", re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    ("FUNCTION", re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    # Match PACKAGE BODY first so the package name is captured (not the BODY keyword).
    ("PACKAGE", re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?PACKAGE\s+BODY\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    ("PACKAGE", re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?PACKAGE\s+(?!BODY\b)([A-Z0-9_$#.]+)", re.IGNORECASE)),
    ("TRIGGER", re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    ("TABLE", re.compile(r"\bCREATE\s+TABLE\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    ("VIEW", re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    ("SYNONYM", re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?SYNONYM\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    ("SEQUENCE", re.compile(r"\bCREATE\s+SEQUENCE\s+([A-Z0-9_$#.]+)", re.IGNORECASE)),
    (
        "MATERIALIZED VIEW",
        re.compile(r"\bCREATE\s+MATERIALIZED\s+VIEW\s+([A-Z0-9_$#.]+)", re.IGNORECASE),
    ),
]

TABLE_REF_PATTERNS = [
    re.compile(r"\bINSERT\s+INTO\s+([A-Z0-9_$#.]+)", re.IGNORECASE),
    # Avoid trigger clauses like "UPDATE ON" and malformed captures like "UPDATE SET".
    re.compile(r"\bUPDATE\s+(?!ON\b|SET\b)([A-Z0-9_$#.]+)", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\s+([A-Z0-9_$#.]+)", re.IGNORECASE),
    re.compile(r"\bFROM\s+([A-Z0-9_$#.]+)", re.IGNORECASE),
    re.compile(r"\bJOIN\s+([A-Z0-9_$#.]+)", re.IGNORECASE),
    re.compile(r"\bMERGE\s+INTO\s+([A-Z0-9_$#.]+)", re.IGNORECASE),
]

SQL_KEYWORDS = {
    "AS",
    "BEGIN",
    "BODY",
    "BY",
    "END",
    "FOR",
    "FROM",
    "GROUP",
    "INTO",
    "JOIN",
    "ON",
    "SELECT",
    "SET",
    "TABLE",
    "THEN",
    "UPDATE",
    "VALUES",
    "WHERE",
}


def normalize_object_name(raw_name: str) -> str:
    return raw_name.strip('"').upper()


def is_valid_object_name(object_name: str) -> bool:
    return bool(object_name) and object_name not in SQL_KEYWORDS


def collect_sql_files(samples_dir: Path) -> list[Path]:
    return sorted(path for path in samples_dir.rglob("*.sql") if path.is_file())


def normalize_output_path(raw_output: str) -> Path:
    output_path = Path(raw_output)
    suffix = output_path.suffix.lower()

    # Accept common HTML extensions; autocorrect common typo ".hmtl" and missing extension.
    if suffix not in {".html", ".htm"}:
        output_path = output_path.with_suffix(".html")

    return output_path


def discover_objects(sql_files: list[Path]) -> dict[str, str]:
    discovered: dict[str, str] = {}

    for sql_file in sql_files:
        text = sql_file.read_text(encoding="utf-8", errors="ignore")

        for object_type, pattern in DDL_PATTERNS:
            for match in pattern.finditer(text):
                object_name = normalize_object_name(match.group(1))
                if not is_valid_object_name(object_name):
                    continue
                discovered[object_name] = object_type

        for pattern in TABLE_REF_PATTERNS:
            for match in pattern.finditer(text):
                object_name = normalize_object_name(match.group(1))
                if not is_valid_object_name(object_name):
                    continue
                discovered.setdefault(object_name, "TABLE")

    for sql_file in sql_files:
        text = sql_file.read_text(encoding="utf-8", errors="ignore")
        has_ddl = any(pattern.search(text) for _, pattern in DDL_PATTERNS)
        if not has_ddl:
            discovered.setdefault(sql_file.stem.upper(), "SQL")

    return discovered


def discover_primary_object(sql_file: Path) -> tuple[str, str]:
    text = sql_file.read_text(encoding="utf-8", errors="ignore")
    for object_type, pattern in DDL_PATTERNS:
        match = pattern.search(text)
        if match:
            object_name = normalize_object_name(match.group(1))
            if is_valid_object_name(object_name):
                return object_name, object_type
    return sql_file.stem.upper(), "SQL"


def find_references(sql_files: list[Path], objects_by_name: dict[str, str]) -> dict[str, dict[str, list[int]]]:
    refs: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    compiled_patterns = {
        object_name: re.compile(rf"\b{re.escape(object_name)}\b", re.IGNORECASE)
        for object_name in objects_by_name
    }

    for sql_file in sql_files:
        lines = sql_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            for object_name, pattern in compiled_patterns.items():
                if pattern.search(line):
                    refs[object_name][sql_file.name].append(line_number)

    return refs


def merge_line_numbers(file_to_lines: dict[str, list[int]]) -> list[int]:
    return sorted({line for lines in file_to_lines.values() for line in lines})


def line_locations_string(file_to_lines: dict[str, list[int]]) -> str:
    merged = merge_line_numbers(file_to_lines)
    return ",".join(str(num) for num in merged)


def build_html_report(
    objects_by_name: dict[str, str],
    refs: dict[str, dict[str, list[int]]],
    report_title: str,
    output_file_reference: str,
    generated_at_utc: str,
) -> str:
    rows = []
    for object_name in sorted(objects_by_name):
        object_type = objects_by_name[object_name]
        file_to_lines = refs.get(object_name, {})
        ref_count = len(merge_line_numbers(file_to_lines))
        locations = line_locations_string(file_to_lines) if file_to_lines else ""

        rows.append(
            "<tr>"
            f"<td>{html.escape(object_name)}</td>"
            f"<td>{html.escape(object_type)}</td>"
            f"<td>{ref_count}</td>"
            f"<td>{html.escape(locations)}</td>"
            "</tr>"
        )

    table_body = "\n".join(rows)

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{html.escape(report_title)}</title>
  <style>
    :root {{
      --bg: #f7f8fc;
      --surface: #ffffff;
      --ink: #1f2937;
      --muted: #6b7280;
      --accent: #0f766e;
      --border: #d1d5db;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at top right, #d1fae5 0%, var(--bg) 45%);
      min-height: 100vh;
      padding: 24px;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      box-shadow: 0 8px 24px rgba(17, 24, 39, 0.08);
      overflow: hidden;
    }}
    .header {{
      padding: 20px 24px;
      background: linear-gradient(120deg, #134e4a, #0f766e);
      color: #ecfeff;
    }}
    h1 {{
      margin: 0;
      font-size: 1.2rem;
      letter-spacing: 0.02em;
    }}
    .subtitle {{
      margin-top: 6px;
      color: #a7f3d0;
      font-size: 0.9rem;
    }}
    .table-wrap {{
      padding: 16px;
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
    }}
    thead th {{
      text-align: left;
      padding: 12px;
      background: #ecfeff;
      border-bottom: 2px solid var(--border);
      color: #0f172a;
    }}
    tbody td {{
      padding: 10px 12px;
      border-bottom: 1px solid #eef2f7;
      vertical-align: top;
    }}
    tbody tr:hover {{
      background: #f8fafc;
    }}
    .muted {{
      color: var(--muted);
      font-size: 0.84rem;
      padding: 0 16px 16px;
    }}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"header\">
      <h1>{html.escape(report_title)}</h1>
      <div class=\"subtitle\">Object references discovered from SQL samples</div>
    </div>
    <div class=\"table-wrap\">
      <table>
        <thead>
          <tr>
            <th>Object Name</th>
            <th>Object Type</th>
            <th>Reference Count</th>
            <th>File Line Number</th>
          </tr>
        </thead>
        <tbody>
          {table_body}
        </tbody>
      </table>
    </div>
    <div class=\"muted\">Reference count is the number of unique line hits across selected sample scope.</div>
    <div class=\"muted\">Generated at (UTC): {html.escape(generated_at_utc)} | Output file: {html.escape(output_file_reference)}</div>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify DB object references in SQL sample files and generate an HTML report."
    )
    parser.add_argument("--samples", default=".github/agents/sample", help="Folder containing .sql sample files.")
    parser.add_argument(
        "--output",
        default=".github/agents/output/db_object_reference_report.html",
        help="Output HTML file path.",
    )
    parser.add_argument(
        "--object",
        default="",
        help="Optional object token. When provided, output is per sample object with line numbers where this token appears.",
    )
    parser.add_argument("--title", default="DB Object Reference Report", help="HTML report title.")
    args = parser.parse_args()

    samples_dir = Path(args.samples)
    output_path = normalize_output_path(args.output)
    target = args.object.strip().upper()

    if not samples_dir.exists() or not samples_dir.is_dir():
        raise SystemExit(f"Samples folder not found: {samples_dir}")

    sql_files = collect_sql_files(samples_dir)
    if not sql_files:
        raise SystemExit(f"No .sql files found in: {samples_dir}")

    objects_by_name = discover_objects(sql_files)
    refs = find_references(sql_files, objects_by_name)

    if target:
        target_pattern = re.compile(rf"\b{re.escape(target)}\b", re.IGNORECASE)
        scoped_objects: dict[str, str] = {}
        scoped_refs: dict[str, dict[str, list[int]]] = {}

        for sql_file in sql_files:
            lines = sql_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            target_lines = [line_no for line_no, line in enumerate(lines, start=1) if target_pattern.search(line)]
            if not target_lines:
                continue

            primary_name, primary_type = discover_primary_object(sql_file)
            if primary_name == target:
                continue

            scoped_objects[primary_name] = primary_type
            scoped_refs[primary_name] = {sql_file.name: target_lines}

        objects_by_name = dict(sorted(scoped_objects.items()))
        refs = scoped_refs

    if target:
        objects_by_name.pop(target, None)
        refs.pop(target, None)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    output_file_reference = output_path.as_posix()
    html_report = build_html_report(
        objects_by_name,
        refs,
        args.title,
        output_file_reference,
        generated_at_utc,
    )
    output_path.write_text(html_report, encoding="utf-8")

    print(f"Report generated: {output_path}")
    print(f"Objects included: {len(objects_by_name)}")


if __name__ == "__main__":
    main()

