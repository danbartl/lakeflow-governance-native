"""Publish an explicit concept as a native Page. Dry-run unless --apply is supplied."""

import argparse
import json
import re
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Concept(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    concept_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]+$")
    display_name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    body: str = Field(min_length=1)
    synonyms: list[str] = Field(default_factory=list, max_length=50)


def resource(value, prefix):
    if not re.fullmatch(prefix + r"/[0-9a-fA-F-]{36}", value):
        raise ValueError(f"Expected {prefix}/<uuid>")
    UUID(value.split("/")[1])
    return value


def request(concept, domain, page_name=None, request_id=None, publish=False):
    domain = resource(domain, "domains")
    body = {
        "display_name": concept.display_name,
        "description": concept.description,
        "synonyms": concept.synonyms,
        "body": f"<!-- concept-id: {concept.concept_id} -->\n\n{concept.body}\n",
    }
    if page_name:
        page_name = resource(page_name, "pages")
        query = {"update_mask": "display_name,description,synonyms,body"}
        if publish:
            body["state"] = "PUBLISHED"
            query["update_mask"] += ",state"
        return {
            "method": "PATCH",
            "path": f"/api/2.0/knowledge/{page_name}",
            "query": query,
            "body": body,
        }
    if not request_id or UUID(request_id).version != 4:
        raise ValueError("Create requires a retained UUIDv4 request-id for safe retries")
    body.update(domain=domain, state="PUBLISHED" if publish else "DRAFT")
    return {
        "method": "POST",
        "path": "/api/2.0/knowledge/pages",
        "query": {"request_id": str(UUID(request_id))},
        "body": body,
    }


def apply(client, prepared, concept, domain):
    if prepared["method"] == "PATCH":
        current = client.do("GET", prepared["path"])
        marker = f"<!-- concept-id: {concept.concept_id} -->"
        if current.get("domain") != domain or not current.get("body", "").startswith(marker + "\n"):
            raise ValueError("Page domain or concept ID differs; refusing to overwrite")
    return client.do(**prepared)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("concept", type=Path)
    parser.add_argument("--domain", required=True)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--request-id", help="New UUIDv4 for create; retain for retries")
    operation.add_argument("--page-name", help="Existing pages/<uuid> for update")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--profile")
    args = parser.parse_args()
    concept = Concept.model_validate_json(args.concept.read_text(encoding="utf-8"))
    prepared = request(concept, args.domain, args.page_name, args.request_id, args.publish)
    if args.apply:
        from databricks.sdk import WorkspaceClient

        result = apply(
            WorkspaceClient(profile=args.profile).api_client, prepared, concept, args.domain
        )
    else:
        result = {"dry_run": True, **prepared}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
