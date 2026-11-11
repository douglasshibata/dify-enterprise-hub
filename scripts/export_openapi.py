"""Export OpenAPI schema for Dify Custom Tools integration.

Run this script to generate `openapi.yaml` and `openapi.json`,
which can be imported directly into Dify via Tools -> Custom -> Create Custom Tool.
"""

from __future__ import annotations

import json
from pathlib import Path
import yaml
from app.main import app

def export_openapi_specs():
    out_dir = Path(__file__).resolve().parent.parent
    openapi_schema = app.openapi()

    # Save as JSON
    json_path = out_dir / "openapi.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    print(f"Exported JSON OpenAPI schema to: {json_path}")

    # Save as YAML
    yaml_path = out_dir / "openapi.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(openapi_schema, f, allow_unicode=True, sort_keys=False)
    print(f"Exported YAML OpenAPI schema to: {yaml_path}")

if __name__ == "__main__":
    export_openapi_specs()
