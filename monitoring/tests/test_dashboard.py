import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "dashboard_build", Path(__file__).parents[1] / "build.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PIPELINE = "12345678-1234-4234-8234-123456789012"


def test_dashboard_is_scoped_and_each_widget_has_a_dataset():
    board = module.build("1234", PIPELINE)
    names = {d["name"] for d in board["datasets"]}
    for dataset in board["datasets"]:
        sql = "".join(dataset["queryLines"])
        assert "workspace_id = '1234'" in sql
        assert f"pipeline_id = '{PIPELINE}'" in sql
        assert "__WORKSPACE_ID__" not in sql
        assert "INTERVAL 7 DAYS" in sql
    for item in board["pages"][0]["layout"]:
        query = item["widget"]["queries"][0]["query"]
        assert query["datasetName"] in names
        assert query["fields"]
    health = "".join(board["datasets"][0]["queryLines"])
    assert "NO_EVENTS" in health
    assert "NOT_A_QUALITY_APPROVAL" in health


@pytest.mark.parametrize("workspace,pipeline", [("1' OR true", PIPELINE), ("1", "all")])
def test_scope_cannot_be_sql_or_unbounded(workspace, pipeline):
    with pytest.raises(ValueError):
        module.build(workspace, pipeline)
