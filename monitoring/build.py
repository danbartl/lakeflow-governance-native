"""Build one scoped native dashboard; no remote calls or custom event collector."""

import argparse
import json
import re
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parent
TABLES = {
    "health": (
        "Betriebsstatus",
        {
            "event_count": "integer",
            "error_events": "integer",
            "last_event": "string",
            "evidence_status": "string",
        },
    ),
    "quality": (
        "Datenqualitaet je Lauf",
        {
            "workspace_id": "string",
            "pipeline_id": "string",
            "update_id": "string",
            "dataset_name": "string",
            "rule_name": "string",
            "passed_records": "integer",
            "failed_records": "integer",
        },
    ),
    "errors": (
        "Fehler",
        {
            "workspace_id": "string",
            "pipeline_id": "string",
            "update_id": "string",
            "event_time": "string",
            "message": "string",
        },
    ),
}


def build(workspace_id, pipeline_id):
    if not re.fullmatch(r"[0-9]+", workspace_id):
        raise ValueError("workspace_id must be numeric")
    pipeline_id = str(UUID(pipeline_id))
    datasets, layout = [], []
    for index, (name, (title, columns)) in enumerate(TABLES.items()):
        sql = (ROOT / "queries" / f"{name}.sql").read_text(encoding="utf-8")
        sql = sql.replace("__WORKSPACE_ID__", workspace_id).replace("__PIPELINE_ID__", pipeline_id)
        datasets.append({"name": name, "displayName": title, "queryLines": sql.splitlines(True)})
        layout.append(
            {
                "widget": {
                    "name": name,
                    "queries": [
                        {
                            "name": "main_query",
                            "query": {
                                "datasetName": name,
                                "disaggregated": True,
                                "fields": [{"name": c, "expression": f"`{c}`"} for c in columns],
                            },
                        }
                    ],
                    "spec": {
                        "version": 1,
                        "widgetType": "table",
                        "encodings": {
                            "columns": [
                                {
                                    "fieldName": c,
                                    "title": c,
                                    "type": dtype,
                                    "displayAs": "number" if dtype == "integer" else "string",
                                    "visible": True,
                                    "order": i,
                                }
                                for i, (c, dtype) in enumerate(columns.items())
                            ]
                        },
                        "frame": {"showTitle": True, "title": title},
                        "itemsPerPage": 25,
                        "condensed": True,
                    },
                },
                "position": {"x": 0, "y": index * 6, "width": 6, "height": 6},
            }
        )
    return {
        "datasets": datasets,
        "pages": [
            {
                "name": "pipeline_quality",
                "displayName": "Pipeline Quality",
                "pageType": "PAGE_TYPE_CANVAS",
                "layout": layout,
            }
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--pipeline-id", required=True)
    args = parser.parse_args()
    dashboard = build(args.workspace_id, args.pipeline_id)
    output = ROOT / ".databricks/board.lvdash.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")
    print(output)
