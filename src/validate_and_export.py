from __future__ import annotations

import json
import sys
from pathlib import Path

from src.validators import DataValidator
from src.exporters import DataExporter

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
PARSED_DIR = BASE_DIR / "output" / "parsed"
EXPORT_DIR = BASE_DIR / "output" / "export"

validator = DataValidator(PARSED_DIR)
report = validator.run()
report_path = PARSED_DIR / "validation_report.json"
validator.write_report(report, report_path)
print(f"Validation report -> {report_path}")
print(f"Invalid comics: {report['summary']['invalid_comics']}")
print(f"Invalid volumes: {report['summary']['invalid_volumes']}")
print(f"Invalid gifts: {report['summary']['invalid_gifts']}")
print(f"Warnings: {report['summary']['warnings']}")

items = validator.load_parsed()
exporter = DataExporter(PARSED_DIR, EXPORT_DIR)
paths = exporter.export_all(items)
for name, path in paths.items():
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"Exported {name} -> {path} ({len(data)} rows)")
